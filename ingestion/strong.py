"""Strong workout-log extractor.

The Strong CSV is one row per set. We keep the set-level grain (the natural unit
for computing training volume = weight x reps), parse the timestamp, and drop
warm-up-only noise downstream rather than here. Output:
``data/raw/strong/sets.parquet``.

Note: Strong logging starts 2026-04-16, while the DEXA window is 2026-04-02 to
2026-05-02 — only part of the window has logged lifts. That mismatch is carried
as a documented caveat in the silver layer, not silently dropped.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import polars as pl

from ingestion.config import STRONG_CSV, bronze_path, get_logger

logger = get_logger("ingestion.strong")


@dataclass(slots=True)
class WorkoutSet:
    """One logged set."""

    performed_at: datetime
    workout_name: str
    exercise_name: str
    set_order: str
    weight_lbs: float
    reps: float
    rpe: float | None


def _parse_ts(raw: str) -> datetime | None:
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.debug("bad timestamp: %r", raw)
        return None


def _to_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class StrongExtractor:
    """Parse the Strong export into set-level records."""

    def __init__(self, csv_path: Path = STRONG_CSV) -> None:
        self.csv_path = csv_path

    def sets(self) -> Iterator[WorkoutSet]:
        df = pl.read_csv(self.csv_path)
        for row in df.iter_rows(named=True):
            ts = _parse_ts(str(row["Date"]))
            if ts is None:
                continue
            yield WorkoutSet(
                performed_at=ts,
                workout_name=str(row.get("Workout Name", "")).strip('"'),
                exercise_name=str(row.get("Exercise Name", "")).strip('"'),
                set_order=str(row.get("Set Order", "")),
                weight_lbs=_to_float(row.get("Weight")) or 0.0,
                reps=_to_float(row.get("Reps")) or 0.0,
                rpe=_to_float(row.get("RPE")),
            )


def run() -> int:
    """Write set-level Parquet. Returns row count."""
    rows = [asdict(s) for s in StrongExtractor().sets()]
    df = pl.DataFrame(rows)
    target = bronze_path("strong") / "sets.parquet"
    df.write_parquet(target)
    logger.info("wrote %d sets -> %s", df.height, target.name)
    return df.height


if __name__ == "__main__":
    run()
