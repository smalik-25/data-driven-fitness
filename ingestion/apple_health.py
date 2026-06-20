"""Apple Health export extractor.

The ``export.xml`` is ~328 MB, so it is parsed with ``lxml.iterparse`` and each
element is cleared after use — memory stays flat regardless of file size, rather
than building a 328 MB DOM. We keep only the record types relevant to the project
and write one Parquet file per metric into ``data/raw/apple_health/``.

Note on protein: LoseIt also syncs ``DietaryProtein``/``DietaryEnergyConsumed``
into Apple Health, but those values are inflated (~150-230 g/day vs ~90-125 g/day
in the per-entry food logs — likely double-counted on sync). The canonical
protein source is therefore the LoseIt ``food-logs.csv`` (see
:mod:`ingestion.loseit`); the Apple Health nutrition records are kept here only
as a downstream cross-check.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import polars as pl
from lxml import etree

from ingestion.config import APPLE_HEALTH_XML, bronze_path, get_logger

logger = get_logger("ingestion.apple_health")

# Map verbose HealthKit identifiers -> short, file-friendly metric names.
QUANTITY_TYPES: dict[str, str] = {
    "HKQuantityTypeIdentifierActiveEnergyBurned": "active_energy",
    "HKQuantityTypeIdentifierBasalEnergyBurned": "basal_energy",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierHeartRate": "heart_rate",
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_heart_rate",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv_sdnn",
    "HKQuantityTypeIdentifierVO2Max": "vo2max",
    "HKQuantityTypeIdentifierDietaryProtein": "dietary_protein",
    "HKQuantityTypeIdentifierDietaryEnergyConsumed": "dietary_energy",
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep",
}

_DATE_FMT = "%Y-%m-%d %H:%M:%S %z"


@dataclass(slots=True)
class HealthRecord:
    """One Apple Health ``<Record>`` reduced to the fields we use."""

    metric: str
    source_name: str | None
    unit: str | None
    start_date: datetime | None
    end_date: datetime | None
    value_num: float | None
    value_str: str | None


def _parse_dt(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, _DATE_FMT)
    except ValueError:
        logger.debug("unparseable date: %r", raw)
        return None


def _coerce_value(raw: str | None) -> tuple[float | None, str | None]:
    """Numeric metrics return (float, None); categorical (e.g. sleep) return (None, str)."""
    if raw is None:
        return None, None
    try:
        return float(raw), None
    except ValueError:
        return None, raw


class AppleHealthExtractor:
    """Stream ``export.xml`` and yield the records we care about."""

    def __init__(self, xml_path: Path = APPLE_HEALTH_XML) -> None:
        self.xml_path = xml_path

    def records(self) -> Iterator[HealthRecord]:
        """Yield filtered :class:`HealthRecord`s, clearing the tree as we go."""
        if not self.xml_path.exists():
            raise FileNotFoundError(f"Apple Health export not found: {self.xml_path}")

        context = etree.iterparse(
            str(self.xml_path), events=("end",), tag="Record", recover=True
        )
        kept = 0
        seen = 0
        for _event, elem in context:
            seen += 1
            metric = QUANTITY_TYPES.get(elem.get("type", ""))
            if metric is not None:
                try:
                    value_num, value_str = _coerce_value(elem.get("value"))
                    yield HealthRecord(
                        metric=metric,
                        source_name=elem.get("sourceName"),
                        unit=elem.get("unit"),
                        start_date=_parse_dt(elem.get("startDate")),
                        end_date=_parse_dt(elem.get("endDate")),
                        value_num=value_num,
                        value_str=value_str,
                    )
                    kept += 1
                except (ValueError, TypeError) as exc:  # never crash the whole run
                    logger.warning("skipping malformed record: %s", exc)
            # Free memory: clear the element and any already-processed siblings.
            elem.clear()
            parent = elem.getparent()
            if parent is not None:
                while elem.getprevious() is not None:
                    del parent[0]
        logger.info("scanned %d records, kept %d", seen, kept)


def run() -> dict[str, int]:
    """Extract Apple Health records and write one Parquet per metric.

    Returns a ``{metric: row_count}`` summary.
    """
    extractor = AppleHealthExtractor()
    buffers: dict[str, list[dict]] = defaultdict(list)
    for rec in extractor.records():
        buffers[rec.metric].append(asdict(rec))

    out_dir = bronze_path("apple_health")
    counts: dict[str, int] = {}
    for metric, rows in buffers.items():
        df = pl.DataFrame(rows)
        target = out_dir / f"{metric}.parquet"
        df.write_parquet(target)
        counts[metric] = df.height
        logger.info("wrote %s rows -> %s", df.height, target.name)
    return counts


if __name__ == "__main__":
    summary = run()
    logger.info("apple_health done: %s", summary)
