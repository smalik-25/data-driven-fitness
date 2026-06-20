"""NHANES population-benchmark extractor.

Downloads the NHANES DXA body-composition (``DXX``) and demographics (``DEMO``)
files for the configured cycle and loads the SAS XPORT (``.XPT``) files with
``pandas.read_sas``. These give a national reference distribution to score my own
DEXA numbers against (e.g. lean/fat percentile for my age and sex).

Network note: NHANES is downloaded from wwwn.cdc.gov. Run this on your machine
(``python -m ingestion.nhanes``); it is intentionally NOT triggered by the
default local-only ingestion run. Files are cached under ``data/raw/nhanes/`` so
re-runs don't re-download.

Codebook: https://wwwn.cdc.gov/nchs/nhanes/  (verify column names per cycle).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

from ingestion.config import bronze_path, get_logger

logger = get_logger("ingestion.nhanes")

# Cycle 2017-2018 uses the "_J" suffix. DXX = whole-body DXA, DEMO = demographics.
NHANES_CYCLE = "2017-2018"
NHANES_SUFFIX = "J"
NHANES_BASE = "https://wwwn.cdc.gov/Nchs/Nhanes"

# Curated columns. SEQN is the respondent join key. Verify against the codebook
# for the chosen cycle — DXA variable names vary slightly across cycles.
DEMO_COLS = {
    "SEQN": "respondent_id",
    "RIAGENDR": "sex",      # 1 = male, 2 = female
    "RIDAGEYR": "age_years",
}
DXX_COLS = {
    "SEQN": "respondent_id",
    "DXDTOPF": "total_body_fat_pct",
    "DXDTOFAT": "total_fat_g",
    "DXDTOLI": "total_lean_g",
    "DXDTRFAT": "trunk_fat_g",
    "DXDTRLI": "trunk_lean_g",
}


def _download(file_stem: str, dest: Path) -> Path:
    """Download one NHANES XPT file if not already cached."""
    target = dest / f"{file_stem}.XPT"
    if target.exists():
        logger.info("cached: %s", target.name)
        return target
    url = f"{NHANES_BASE}/{NHANES_CYCLE}/{file_stem}.XPT"
    logger.info("downloading %s", url)
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    target.write_bytes(resp.content)
    return target


def _load_xpt(path: Path, col_map: dict[str, str]) -> pd.DataFrame:
    """Read an XPT file and keep/rename the curated columns that exist."""
    df = pd.read_sas(path, format="xport")
    present = {src: dst for src, dst in col_map.items() if src in df.columns}
    missing = set(col_map) - set(present)
    if missing:
        logger.warning("%s missing columns: %s", path.name, sorted(missing))
    return df[list(present)].rename(columns=present)


def run() -> int:
    """Download + join NHANES DXA and demographics. Returns row count."""
    out = bronze_path("nhanes")
    demo = _load_xpt(_download(f"DEMO_{NHANES_SUFFIX}", out), DEMO_COLS)
    dxx = _load_xpt(_download(f"DXX_{NHANES_SUFFIX}", out), DXX_COLS)
    merged = demo.merge(dxx, on="respondent_id", how="inner")
    merged.to_parquet(out / "bodycomp.parquet", index=False)
    logger.info("wrote %d NHANES rows -> bodycomp.parquet", len(merged))
    return len(merged)


if __name__ == "__main__":
    run()
