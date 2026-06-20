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

import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

import pdfplumber
import polars as pl

from ingestion.config import DEXA_PDFS, bronze_path, get_logger

logger = get_logger("ingestion.bodyspec")

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
    """Stub BodySpec API client.

    TODO(creds): set ``BODYSPEC_API_TOKEN`` in ``.env`` and implement ``records()``
    against the real endpoint. Until then the PDF parser is the source of truth.
    """

    def __init__(self, token: str | None = None) -> None:
        self.token = token

    def records(self) -> Iterator[RegionalComposition]:  # pragma: no cover - stub
        raise NotImplementedError(
            "BodySpec API not wired yet — provide BODYSPEC_API_TOKEN and the base URL."
        )


def run() -> int:
    """Parse DEXA PDFs and write regional composition to Parquet. Returns row count."""
    rows = [asdict(r) for r in BodySpecPDFParser().records()]
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
