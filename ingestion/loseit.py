"""LoseIt extractor — food logs, calorie summaries, and logged bodyweight.

Three outputs, all written to ``data/raw/loseit/``:

* **food_days** — per-food-entry logs (``food-logs.csv``) aggregated to a daily
  total. This is the source of truth for protein: it is logged per food item and
  is more reliable than the Apple Health ``DietaryProtein`` sync, which is kept
  only as a downstream cross-check. Per project rules, only Date, Calories, and
  Protein are trusted from this file — every other macro column is ignored.
* **calorie_days** — the daily calorie summary (exercise calories, budget).
* **weights** — logged bodyweight time series.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

import polars as pl

from ingestion.config import (
    LOSEIT_CALORIES_CSV,
    LOSEIT_FOOD_LOGS_CSV,
    LOSEIT_WEIGHTS_CSV,
    bronze_path,
    get_logger,
)

logger = get_logger("ingestion.loseit")


@dataclass(slots=True)
class CalorieDay:
    """One day of LoseIt calorie accounting."""

    log_date: date
    food_cals: float
    exercise_cals: float
    budget_cals: float


@dataclass(slots=True)
class FoodDay:
    """One day of food logging, aggregated from individual entries.

    Only Date, Calories, and Protein are trusted (project rule); other macros in
    the source file are ignored.
    """

    log_date: date
    food_calories: float
    protein_g: float
    n_entries: int


@dataclass(slots=True)
class WeightReading:
    """One logged bodyweight value (soft-deleted rows are skipped)."""

    log_date: date
    weight_lbs: float


def _mdY(raw: str) -> date | None:
    try:
        return datetime.strptime(raw.strip(), "%m/%d/%Y").date()
    except ValueError:
        logger.debug("bad date: %r", raw)
        return None


class LoseItExtractor:
    """Parse the LoseIt calorie-summary and weights CSVs."""

    def __init__(
        self,
        calories_csv: Path = LOSEIT_CALORIES_CSV,
        food_logs_csv: Path = LOSEIT_FOOD_LOGS_CSV,
        weights_csv: Path = LOSEIT_WEIGHTS_CSV,
    ) -> None:
        self.calories_csv = calories_csv
        self.food_logs_csv = food_logs_csv
        self.weights_csv = weights_csv

    def food_days(self) -> Iterator[FoodDay]:
        """Aggregate per-entry food logs to a daily total (calories + protein).

        Drops soft-deleted rows; keeps only the trusted columns. Aggregation is
        done in Polars (group_by date) rather than row-by-row.
        """
        df = pl.read_csv(self.food_logs_csv)
        if "Deleted" in df.columns:
            df = df.filter(pl.col("Deleted").cast(pl.Int64, strict=False) == 0)
        daily = (
            df.with_columns(
                pl.col("Date").str.strptime(pl.Date, "%m/%d/%Y", strict=False).alias("log_date"),
                pl.col("Calories").cast(pl.Float64, strict=False).alias("cal"),
                pl.col("Protein (g)").cast(pl.Float64, strict=False).alias("protein"),
            )
            .drop_nulls("log_date")
            .group_by("log_date")
            .agg(
                pl.col("cal").sum().alias("food_calories"),
                pl.col("protein").sum().alias("protein_g"),
                pl.len().alias("n_entries"),
            )
            .sort("log_date")
        )
        for row in daily.iter_rows(named=True):
            yield FoodDay(
                log_date=row["log_date"],
                food_calories=round(row["food_calories"] or 0.0, 1),
                protein_g=round(row["protein_g"] or 0.0, 1),
                n_entries=int(row["n_entries"]),
            )

    def calorie_days(self) -> Iterator[CalorieDay]:
        df = pl.read_csv(self.calories_csv)
        for row in df.iter_rows(named=True):
            d = _mdY(str(row["Date"]))
            if d is None:
                continue
            yield CalorieDay(
                log_date=d,
                food_cals=float(row.get("Food cals", 0) or 0),
                exercise_cals=float(row.get("Exercise cals", 0) or 0),
                budget_cals=float(row.get("Budget cals", 0) or 0),
            )

    def weights(self) -> Iterator[WeightReading]:
        df = pl.read_csv(self.weights_csv)
        for row in df.iter_rows(named=True):
            if str(row.get("Deleted", "false")).lower() == "true":
                continue
            d = _mdY(str(row["Date"]))
            if d is None:
                continue
            yield WeightReading(log_date=d, weight_lbs=float(row["Weight"]))


def run() -> dict[str, int]:
    """Write calorie-day and weight Parquet files. Returns row counts."""
    extractor = LoseItExtractor()
    out = bronze_path("loseit")
    counts: dict[str, int] = {}

    food = [asdict(f) for f in extractor.food_days()]
    pl.DataFrame(food).write_parquet(out / "food_days.parquet")
    counts["food_days"] = len(food)

    cals = [asdict(c) for c in extractor.calorie_days()]
    pl.DataFrame(cals).write_parquet(out / "calorie_days.parquet")
    counts["calorie_days"] = len(cals)

    wts = [asdict(w) for w in extractor.weights()]
    pl.DataFrame(wts).write_parquet(out / "weights.parquet")
    counts["weights"] = len(wts)

    logger.info("wrote %s", counts)
    return counts


if __name__ == "__main__":
    run()
