# Devlog

A first-person, append-only build log — one entry per work session. Explains what
was built **and why**, not just what changed. Raw material for project writeups
and interview talking points.

---

## Entry template

```
## YYYY-MM-DD — <short title>

**What I built**
-

**Why I made these decisions**
-

**What I learned or got stuck on**
-

**Next up**
-
```

---

## 2026-06-20 — Phase 0: project scaffold

**What I built**
- Scaffolded the repo structure: `ingestion/` (six source modules), `analysis/`
  (five questions + the measurement-uncertainty centerpiece), `dbt_project/`,
  `airflow/dags/`, `dashboard/`, `warehouse/`, `docs/`, `tests/`, CI workflow dir.
- Wrote a hardened `.gitignore` that excludes all raw health data (Apple Health
  export, DEXA PDFs, source CSVs), `*.duckdb`, secrets, and `profiles.yml`.
- README with the measurement-uncertainty framing, tech-stack table, and a
  phase progress checklist; this DEVLOG; `requirements.txt`, `pyproject.toml`,
  `Makefile`.

**Why I made these decisions**
- gitignore came first, before any `git add` — this is identifying health data
  and git history is effectively permanent, so the cost of a mistake is high.
- DuckDB for local dev + BigQuery as the prod target (one dbt project, two
  targets). Not a scale decision — at this data volume DuckDB is plenty — but a
  privacy + dev/prod-parity one: private raw data stays local, only
  de-identified marts reach the cloud and the public dashboard.
- Led the README with the implausible DEXA delta on purpose. The headline of
  this project is interrogating the instrument, not celebrating a recomp.

**What I learned or got stuck on**
- The local folder wasn't a git repo yet (the GitHub repo existed remotely but
  unconnected), so Phase 0 includes `git init` + remote wiring.

**Next up**
- Phase 1: streaming parse of the 328 MB Apple Health `export.xml` into
  partitioned Parquet, plus the other five source extractors.

---

## 2026-06-20 — Phase 1: ingestion layer → bronze

**What I built**
- Six source extractors, each with a record dataclass + a generator-based
  parser, real logging, and per-record error handling:
  - `apple_health.py` — streaming `lxml.iterparse` over the 328 MB export with
    element clearing; whitelists 10 metric types → one Parquet per metric.
  - `bodyspec.py` — `pdfplumber` regex parse of the DEXA regional tables (PDF
    path working; API client stubbed pending a token).
  - `loseit.py` — calorie-day + weight Parquet.
  - `strong.py` — set-level Parquet (volume = weight × reps).
  - `nhanes.py` — XPT downloader + `read_sas` loader (network, run on demand).
  - `acsm.py` — small versioned reference table of protein/volume ranges.
- `run_ingestion.py` orchestrator (local sources by default, NHANES behind
  `--with-nhanes`). Ran end to end against real data; ruff clean, pytest green.

**Why I made these decisions**
- `iterparse` + `elem.clear()` was non-negotiable for the 328 MB file — it keeps
  the DOM flat. Measured: ~18 s, peak RSS ~0.5 GB (just the buffered records),
  376k of 770k records kept.
- Protein sourcing: the daily-calorie-summary CSV has no protein, and the Apple
  Health `DietaryProtein` sync turned out to be **inflated** (~150–230 g/day).
  Sam then provided `food-logs.csv` (per-food-entry logs); aggregating those by
  date in Polars gives ~90–125 g/day — the reliable signal. So `food-logs.csv`
  is now the canonical protein + food-calorie source (trusting only Date,
  Calories, Protein per project rule); Apple Health protein is kept as a
  cross-check. The ~40–50% gap between the two sources is itself a finding worth
  surfacing in the analysis.
- NHANES kept behind a flag so the everyday run stays offline and fast, and so
  no network is required to reproduce the personal-data pipeline.
- Verified extraction against ground truth: DEXA totals match the PDFs exactly
  (lean 119.5 → 127.9 lb), giving confidence the regex parse is correct.

**What I learned or got stuck on**
- Sandbox can't run git on the mounted folder (leaves stale `.lock` files), so
  all git is handed to me as copy-paste commands now — captured as a project
  convention.

**Next up**
- Phase 2: DuckDB warehouse + dbt staging/silver at a daily grain; wire the
  two dbt targets (DuckDB dev / BigQuery prod) and the exercise→region map.

---

## 2026-06-20 — Phase 2: DuckDB warehouse + dbt silver

**What I built**
- dbt project (dbt-duckdb) with two targets wired in `profiles.yml`: `dev` →
  DuckDB, `prod` → BigQuery (unused until Phase 6). `profiles.yml` gitignored;
  committed a `profiles.yml.example`.
- `read_bronze()` macro so staging is the only layer that touches raw Parquet.
- 11 staging views (one per bronze table) + 5 silver tables at a daily grain:
  `silver_daily_energy` (TDEE, intake, net balance), `silver_daily_protein`
  (g, g/kg, with bodyweight carried forward via a DuckDB ASOF join, plus the AH
  cross-check), `silver_daily_recovery`, `silver_daily_training_volume` (by DEXA
  region), and `silver_dexa`.
- `dim_exercise` seed mapping all 38 logged exercises → arms/legs/trunk +
  muscle group. **Shoulders/delts → arms** per Sam's call.
- Tests: built-in not_null/unique/accepted_values + 3 zero-dependency singular
  tests (grain uniqueness ×2, all-exercises-mapped). `dbt build` = PASS 37/37.

**Why I made these decisions**
- Daily grain is the natural join: almost every behavioral source collapses to
  one row per day, and date is the shared key to the (sparse) DEXA outcomes.
- Dropped `dbt_utils` — the sandbox/CI can't reach hub.getdbt.com, so I covered
  grain uniqueness with singular tests instead of an external package. Keeps the
  project reproducible offline.
- ASOF join for bodyweight carry-forward is the clean DuckDB tool; flagged in the
  model + dict that prod/BigQuery needs a `last_value` swap.

**What I learned or got stuck on**
- Early numbers already cohere on the fat side: in-window mean TDEE ≈2994,
  intake ≈1687 → ~−1306 kcal/day deficit. Over the window that implies ~11 lb
  fat loss; DEXA shows −9.8 lb fat — close. The *lean* +8.4 lb is the part energy
  balance can't explain (→ Phase 4). Protein ≈1.83 g/kg, squarely in the ACSM
  hypertrophy range; AH protein ≈260 g confirms its ~2× inflation.
- Had to add a `.gitignore` exception so the broad `*.csv` rule doesn't swallow
  the `dim_exercise` seed.

**Next up**
- Phase 3: gold/marts — `fct_daily`, NHANES/ACSM benchmark dims, the DEXA-change
  + energy-reconciliation marts with the precision band attached.
