"""ACSM / position-stand reference values.

A small, versioned reference table — not downloaded, just encoded from published
guidance so the analysis can benchmark intake and training against established
ranges (e.g. is protein in the hypertrophy range? is volume reasonable?).

Sources to cite in the README/data dictionary:
* ACSM / ISSN protein position stands (hypertrophy ~1.6-2.2 g/kg/day).
* ACSM resistance-training guidance for hypertrophy (sets/reps ranges).

Values here are intentionally conservative ranges; cite the exact source next to
each row when you write the data dictionary.
"""

from __future__ import annotations

import polars as pl

from ingestion.config import bronze_path, get_logger

logger = get_logger("ingestion.acsm")

# (metric, population/context, low, high, unit, source_note)
REFERENCE_ROWS: list[dict] = [
    {
        "metric": "protein_intake",
        "context": "muscle_hypertrophy",
        "low": 1.6,
        "high": 2.2,
        "unit": "g/kg/day",
        "source": "ISSN/ACSM protein position stand",
    },
    {
        "metric": "protein_intake",
        "context": "general_active_adult",
        "low": 1.2,
        "high": 1.6,
        "unit": "g/kg/day",
        "source": "ACSM active-adult guidance",
    },
    {
        "metric": "resistance_sets_per_muscle",
        "context": "hypertrophy_weekly",
        "low": 10.0,
        "high": 20.0,
        "unit": "sets/week",
        "source": "ACSM/ hypertrophy volume guidance",
    },
    {
        "metric": "rep_range",
        "context": "hypertrophy",
        "low": 6.0,
        "high": 12.0,
        "unit": "reps",
        "source": "ACSM resistance-training guidelines",
    },
    {
        "metric": "weight_change_rate",
        "context": "lean_gain_recommended_max",
        "low": 0.25,
        "high": 0.5,
        "unit": "lb/week",
        "source": "Common recomposition guidance (context for plausibility checks)",
    },
]


def run() -> int:
    """Write the ACSM reference table to Parquet. Returns row count."""
    df = pl.DataFrame(REFERENCE_ROWS)
    target = bronze_path("acsm") / "reference.parquet"
    df.write_parquet(target)
    logger.info("wrote %d ACSM reference rows -> %s", df.height, target.name)
    return df.height


if __name__ == "__main__":
    run()
