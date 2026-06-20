"""Shared paths, logging, and constants for the ingestion layer.

All raw source files live in the project root (gitignored). Ingestion writes
bronze Parquet into ``data/raw/<source>/`` (also gitignored). Nothing in this
module loads or processes data — it only defines where things go.
"""

from __future__ import annotations

import logging
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw source files as provided (gitignored — never committed).
APPLE_HEALTH_XML = PROJECT_ROOT / "apple_health_export" / "export.xml"
LOSEIT_CALORIES_CSV = PROJECT_ROOT / "daily-calorie-summary.csv"
LOSEIT_FOOD_LOGS_CSV = PROJECT_ROOT / "food-logs.csv"
LOSEIT_WEIGHTS_CSV = PROJECT_ROOT / "weights.csv"
STRONG_CSV = PROJECT_ROOT / "strong_workouts.csv"
DEXA_PDFS = sorted(PROJECT_ROOT.glob("bodyspec-results*.pdf"))

# Bronze landing zone (gitignored).
BRONZE_DIR = PROJECT_ROOT / "data" / "raw"

# The DEXA scans bracket the high-confidence analysis window.
ANALYSIS_WINDOW_START = "2026-04-02"  # first DEXA scan
ANALYSIS_WINDOW_END = "2026-05-02"  # second DEXA scan


def bronze_path(source: str) -> Path:
    """Return (and create) the bronze output directory for a source."""
    out = BRONZE_DIR / source
    out.mkdir(parents=True, exist_ok=True)
    return out


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger (idempotent across imports)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-7s  %(name)s  %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
