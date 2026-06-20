"""Ingestion entrypoint — run source extractors and land bronze Parquet.

By default this runs the *local* sources (Apple Health, BodySpec PDFs, LoseIt,
Strong, ACSM) which need no network. NHANES is network-bound and is only run when
``--with-nhanes`` is passed, so the common path stays offline and fast.

    python -m ingestion.run_ingestion              # local sources only
    python -m ingestion.run_ingestion --with-nhanes  # also download NHANES
"""

from __future__ import annotations

import argparse

from ingestion import acsm, apple_health, bodyspec, loseit, strong
from ingestion.config import get_logger

logger = get_logger("ingestion.run")


def main(with_nhanes: bool = False) -> dict[str, object]:
    """Run all configured extractors and return a per-source summary."""
    summary: dict[str, object] = {}

    logger.info("=== Apple Health ===")
    summary["apple_health"] = apple_health.run()

    logger.info("=== BodySpec (DEXA PDFs) ===")
    summary["bodyspec"] = bodyspec.run()

    logger.info("=== LoseIt ===")
    summary["loseit"] = loseit.run()

    logger.info("=== Strong ===")
    summary["strong"] = strong.run()

    logger.info("=== ACSM reference ===")
    summary["acsm"] = acsm.run()

    if with_nhanes:
        from ingestion import nhanes  # imported lazily to avoid requiring network

        logger.info("=== NHANES (download) ===")
        summary["nhanes"] = nhanes.run()
    else:
        logger.info("skipping NHANES (pass --with-nhanes to download)")

    logger.info("ingestion complete: %s", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ingestion layer.")
    parser.add_argument(
        "--with-nhanes", action="store_true", help="also download + load NHANES"
    )
    args = parser.parse_args()
    main(with_nhanes=args.with_nhanes)
