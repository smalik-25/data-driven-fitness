"""Shared helpers and constants for the Phase 4 analysis scripts.

Every analysis reads from the DuckDB warehouse built by dbt (gitignored), writes a
figure to ``analysis/outputs/`` (gitignored), and returns a result dict. Constants
that encode physiological / measurement assumptions live here so they are stated
once and unit-tested.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WAREHOUSE = PROJECT_ROOT / "warehouse" / "ddf.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "outputs"

# Analysis window (the two DEXA scans).
WINDOW_START = "2026-04-02"
WINDOW_END = "2026-05-02"
WINDOW_DAYS = 30

# --- Energy balance ---------------------------------------------------------
KCAL_PER_LB_FAT = 3500.0  # classic approximation for fat mass change

# --- DEXA measurement assumptions -------------------------------------------
# Random precision (coefficient of variation per scan). Mirrors the dbt vars.
LEAN_CV = 0.01
FAT_CV = 0.015

# Hydration sensitivity, from BodySpec's own gallon-of-water experiment
# (docs/measurement_notes.md): one gallon of water shifted the DEXA reading by...
LEAN_LB_PER_GALLON = 7.4
FAT_LB_PER_GALLON = -1.0
BODYFAT_PCT_PER_GALLON = -1.0
LB_WATER_PER_GALLON = 8.345

# Plausible REAL muscle-gain rate. Sam started consistent weight training right
# after scan 1, so he's an untrained beginner — "newbie gains" are fastest in the
# first weeks. Untrained males credibly gain ~0.5-1.0 lb of muscle/week early on
# (BodySpec recomp client managed 5.6 lb / 6 wk ≈ 0.93). We use 1.0 lb/wk as a
# generous upper bound for the ~30-day window (≈ 4 lb).
NEWBIE_MUSCLE_LB_PER_WEEK_MAX = 1.0
TRAINING_START = "2026-04-02"  # began ~scan 1; Strong logging starts 2026-04-16


def connect() -> duckdb.DuckDBPyConnection:
    """Open the warehouse read-only. Errors clearly if dbt hasn't been run."""
    if not WAREHOUSE.exists():
        raise FileNotFoundError(
            f"Warehouse not found at {WAREHOUSE}. Run `make build` (dbt) first."
        )
    return duckdb.connect(str(WAREHOUSE), read_only=True)


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def lean_precision_band95(lean_t0: float, lean_t1: float, cv: float = LEAN_CV) -> float:
    """95% band on a lean delta from two independent scans with CV ``cv``."""
    sd = ((cv * lean_t0) ** 2 + (cv * lean_t1) ** 2) ** 0.5
    return 1.96 * sd


def gallons_equivalent(lean_delta_lbs: float) -> float:
    """Express a lean change as the number of gallons of water that would mimic it."""
    return lean_delta_lbs / LEAN_LB_PER_GALLON
