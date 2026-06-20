"""BodySpec DEXA extractor.

Two paths to the same data:

* :class:`BodySpecPDFParser` — parses the regional-assessment table out of the
  DEXA result PDFs with ``pdfplumber``. This is the default and needs no
  credentials.
* :class:`BodySpecAPIClient` — stub for the BodySpec API. Fill in the base URL,
  auth, and response mapping once credentials are available (see ``run`` note).

Each scan produces five regional rows (arms / legs / trunk / android / gynoid)
plus a total, written to ``data/raw/bodyspec/regional.parquet``.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

import pdfplumber
import polars as pl
import requests

from ingestion.config import DEXA_PDFS, bronze_path, get_logger

logger = get_logger("ingestion.bodyspec")

KG_TO_LB = 2.20462
BODYSPEC_BASE_URL = "https://app.bodyspec.com"
_MASS_KEYS = ("fat_mass_kg", "lean_mass_kg", "bone_mass_kg", "total_mass_kg")

_REGIONS = ("Arms", "Legs", "Trunk", "Android", "Gynoid", "Total")
# e.g. "Arms 21.4% 18.2 3.9 13.5 0.7"
_REGION_RE = re.compile(
    r"^(?P<region>\w+)\s+(?P<fat_pct>[\d.]+)%\s+(?P<total_mass>[\d.]+)\s+"
    r"(?P<fat_lbs>[\d.]+)\s+(?P<lean_lbs>[\d.]+)\s+(?P<bmc>[\d.]+)$"
)
# e.g. "M, Sam Male 10/25/2004 70.0 in. 160.0 lbs. 4/2/2026"
_DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*$")


@dataclass(slots=True)
class RegionalComposition:
    """One body region's composition from a single DEXA scan."""

    scan_date: date
    region: str
    fat_pct: float
    total_mass_lbs: float
    fat_mass_lbs: float
    lean_mass_lbs: float
    bmc_lbs: float


class BodySpecPDFParser:
    """Extract regional composition rows from BodySpec result PDFs."""

    def __init__(self, pdf_paths: list[Path] | None = None) -> None:
        self.pdf_paths = pdf_paths if pdf_paths is not None else DEXA_PDFS

    def _scan_date(self, text: str) -> date | None:
        for line in text.splitlines():
            if line.startswith("M, Sam") or "Measured Date" in line:
                m = _DATE_RE.search(line.strip())
                if m:
                    return datetime.strptime(m.group(1), "%m/%d/%Y").date()
        return None

    def records(self) -> Iterator[RegionalComposition]:
        for pdf_path in self.pdf_paths:
            if not pdf_path.exists():
                logger.warning("missing DEXA PDF: %s", pdf_path)
                continue
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            scan_date = self._scan_date(full_text)
            if scan_date is None:
                logger.warning("no measured date found in %s", pdf_path.name)
                continue
            found = 0
            for line in full_text.splitlines():
                m = _REGION_RE.match(line.strip())
                if m and m.group("region") in _REGIONS:
                    yield RegionalComposition(
                        scan_date=scan_date,
                        region=m.group("region"),
                        fat_pct=float(m.group("fat_pct")),
                        total_mass_lbs=float(m.group("total_mass")),
                        fat_mass_lbs=float(m.group("fat_lbs")),
                        lean_mass_lbs=float(m.group("lean_lbs")),
                        bmc_lbs=float(m.group("bmc")),
                    )
                    found += 1
            logger.info("%s: %d regional rows (scan %s)", pdf_path.name, found, scan_date)


class BodySpecAPIClient:
    """BodySpec REST client (Bearer JWT), per the published OpenAPI spec.

    Flow: list the user's results, then fetch each result's DEXA composition and
    map it to the same :class:`RegionalComposition` shape the PDF parser yields.
    The API returns masses in **kg** (converted to lbs here) and splits arms/legs
    into left/right (summed here into combined ``arms``/``legs`` to match the PDF
    regional breakdown).

    Auth: set ``BODYSPEC_API_TOKEN`` (a JWT) in the environment or ``.env``.
    Endpoints used:
      GET /api/v1/users/me/results/
      GET /api/v1/users/me/results/{result_id}/dexa/composition
    """

    def __init__(
        self,
        token: str | None = None,
        base_url: str = BODYSPEC_BASE_URL,
        timeout: int = 30,
    ) -> None:
        self.token = token or os.environ.get("BODYSPEC_API_TOKEN")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        if not self.token:
            raise ValueError("BodySpec API token missing: set BODYSPEC_API_TOKEN")

    def _get(self, path: str, **params: object) -> dict:
        resp = requests.get(
            f"{self.base_url}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
            params=params or None,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def _list_results(self) -> Iterator[dict]:
        page = self._get("/api/v1/users/me/results/")
        yield from page.get("results", [])

    @staticmethod
    def _to_row(scan_date: date, region: str, obj: dict) -> RegionalComposition:
        def lb(key: str) -> float:
            return round((obj.get(key) or 0.0) * KG_TO_LB, 2)

        return RegionalComposition(
            scan_date=scan_date,
            region=region,
            fat_pct=obj.get("region_fat_pct") or 0.0,
            total_mass_lbs=lb("total_mass_kg"),
            fat_mass_lbs=lb("fat_mass_kg"),
            lean_mass_lbs=lb("lean_mass_kg"),
            bmc_lbs=lb("bone_mass_kg"),
        )

    @staticmethod
    def _combine(a: dict, b: dict) -> dict:
        """Sum two body regions (e.g. left+right arm) and recompute fat %."""
        merged = {k: (a.get(k) or 0.0) + (b.get(k) or 0.0) for k in _MASS_KEYS}
        total = merged["total_mass_kg"] or 1.0
        merged["region_fat_pct"] = round(100 * merged["fat_mass_kg"] / total, 2)
        return merged

    def _region_rows(self, scan_date: date, comp: dict) -> Iterator[RegionalComposition]:
        regions = comp.get("regions", {})
        if "left_arm" in regions and "right_arm" in regions:
            arms = self._combine(regions["left_arm"], regions["right_arm"])
            yield self._to_row(scan_date, "arms", arms)
        if "left_leg" in regions and "right_leg" in regions:
            legs = self._combine(regions["left_leg"], regions["right_leg"])
            yield self._to_row(scan_date, "legs", legs)
        for special in ("trunk", "android", "gynoid"):
            if special in regions:
                yield self._to_row(scan_date, special, regions[special])
        if comp.get("total"):
            yield self._to_row(scan_date, "total", comp["total"])

    def records(self) -> Iterator[RegionalComposition]:
        for result in self._list_results():
            result_id = result["result_id"]
            scan_date = datetime.fromisoformat(
                result["start_time"].replace("Z", "+00:00")
            ).date()
            comp = self._get(f"/api/v1/users/me/results/{result_id}/dexa/composition")
            try:
                yield from self._region_rows(scan_date, comp)
            except (KeyError, TypeError) as exc:  # never crash the whole run
                logger.warning("skipping result %s: %s", result_id, exc)


def run(use_api: bool | None = None) -> int:
    """Write DEXA regional composition to Parquet. Returns row count.

    Uses the API when a BODYSPEC_API_TOKEN is set (or ``use_api=True``), else the
    PDF parser (the verified default that needs no credentials).
    """
    if use_api is None:
        use_api = bool(os.environ.get("BODYSPEC_API_TOKEN"))
    source = BodySpecAPIClient() if use_api else BodySpecPDFParser()
    logger.info("DEXA source: %s", type(source).__name__)
    rows = [asdict(r) for r in source.records()]
    if not rows:
        logger.warning("no DEXA rows extracted")
        return 0
    df = pl.DataFrame(rows)
    target = bronze_path("bodyspec") / "regional.parquet"
    df.write_parquet(target)
    logger.info("wrote %d rows -> %s", df.height, target.name)
    return df.height


if __name__ == "__main__":
    run()
