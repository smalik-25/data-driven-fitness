"""Export the de-identified, dashboard-only tables into a small committed DuckDB.

The full warehouse (warehouse/ddf.duckdb) is gitignored and stays local. The
public site and Netlify CI build from this slim copy, which contains ONLY the
aggregate marts/dims the Evidence pages query — no raw data, no bronze, no
identifying records. Run after `make build`:

    make export-public          # or: python -m scripts.export_public_db

What goes public (Sam's own de-identified daily/region aggregates):
    mart_dexa_change, mart_recomp_reconciliation, silver_dexa,
    silver_daily_training_volume, fct_daily, dim_bodyfat_percentile
"""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "warehouse" / "ddf.duckdb"
DST = ROOT / "dashboard" / "sources" / "ddf" / "public.duckdb"

# Exactly the tables referenced by dashboard/sources/ddf/*.sql.
PUBLIC_TABLES = [
    "mart_dexa_change",
    "mart_recomp_reconciliation",
    "silver_dexa",
    "silver_daily_training_volume",
    "fct_daily",
    "dim_bodyfat_percentile",
]


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"warehouse not found: {SRC} — run `make build` first")
    DST.unlink(missing_ok=True)
    src_path = str(SRC).replace("'", "''")
    con = duckdb.connect(str(DST))
    con.execute(f"attach '{src_path}' as warehouse (read_only)")
    for table in PUBLIC_TABLES:
        con.execute(f"create table {table} as select * from warehouse.{table}")
    con.execute("detach warehouse")
    rows = {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in PUBLIC_TABLES}
    con.close()
    print(f"wrote {len(PUBLIC_TABLES)} tables -> {DST}")
    for table, n in rows.items():
        print(f"  {table}: {n} rows")


if __name__ == "__main__":
    main()
