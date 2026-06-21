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

---

## 2026-06-20 — Phase 3: gold marts + BodySpec API client

**What I built**
- Wired the real **BodySpec API client** from the OpenAPI spec Sam provided:
  Bearer-JWT auth, list results → fetch `/dexa/composition`, map kg→lbs and sum
  left/right arms+legs to match the PDF regional shape. PDF parser stays the
  verified default; API kicks in when `BODYSPEC_API_TOKEN` is set. Spec saved to
  `docs/bodyspec_openapi.json`.
- Gold star schema: `fct_daily` (one-day grain, **enforced dbt contract**)
  joining energy/protein/recovery + training volume pivoted to arms/legs/trunk;
  `dim_date`, `dim_region`, `dim_acsm_targets`; `dim_nhanes_bodycomp` (disabled
  until NHANES is downloaded, via `var('enable_nhanes')`); seed
  `dim_bodyfat_percentile` (population body-fat percentile chart).
- `mart_dexa_change` — per-region lean/fat delta with a 95% uncertainty band
  propagated from CV vars (`lean_cv`, `fat_cv`) and an `is_resolvable` flag.
- `mart_recomp_reconciliation` — the centerpiece, one row. `dbt build` = PASS
  62/62.

**Why I made these decisions**
- Encoded the population benchmark as a committed **seed** (and disabled the raw
  NHANES model) so the project builds fully offline / in CI — the percentile
  chart on the DEXA report is itself NHANES-derived, so it's a legit yardstick.
- Made CV and kcal/lb **dbt vars** so the uncertainty assumptions are explicit
  and tunable, not buried magic numbers.
- Enforced a contract on `fct_daily` so downstream (marts + Phase 4) can trust
  the grain and types.

**What I learned or got stuck on**
- The numbers cohere into the project's thesis. Over 30 logged days the
  cumulative deficit (−39,190 kcal) implies −11.2 lb fat; DEXA shows −9.8 lb (gap
  +1.4 lb — fat reconciles). The **+8.4 lb lean is unexplained by energy
  balance**. At a 1% lean CV the regional gains are "resolvable," yet +8.4 lb
  muscle in a month is biologically impossible → points to calibration/hydration,
  not random error. That tension is the Phase-4 headline.
- Hit a model/seed name collision (`dim_bodyfat_percentile`); the redundant
  passthrough model was deleted (needed the file-delete permission — the mount
  blocks `rm`), keeping the seed as the dimension.

**Next up**
- Phase 4: the analysis scripts — the five questions + the measurement-uncertainty
  centerpiece, with the energy-balance and uncertainty math unit-tested.

---

## 2026-06-21 — Phase 4: analysis + the measurement-uncertainty centerpiece

**What I built**
- `analysis/_common.py` — warehouse connection + the physiological constants
  (kcal/lb, DEXA CVs, the BodySpec hydration coefficients, newbie-muscle bound),
  stated once and unit-tested.
- Six analyses, each writes a figure + prints a result:
  - `measurement_uncertainty.py` (centerpiece) — decomposes the +8.4 lb lean into
    real newbie muscle (≤4.3 lb), glycogen/hydration water (~4.1 lb ≈ 0.56 gal),
    and a random precision band (±3.4 lb).
  - `energy_balance.py`, `regional_hypertrophy.py`, `protein_lean.py`,
    `recovery_load.py`, `volume_efficiency.py`.
- `tests/test_analysis_math.py` — unit tests on the conversions (kcal/lb,
  precision-band propagation, gallon-equivalent, newbie bound). 7/7 pass.

**Why I made these decisions**
- Two BodySpec blog posts Sam found reframed the centerpiece: their gallon-of-
  water experiment gives a real coefficient (7.4 lb lean per gallon), and their
  recomp client shows multi-pound lean swings that are glycogen-water. Combined
  with Sam starting training at scan 1 (newbie gains + training-onset glycogen
  loading), the lean delta is best read as a 3-way mixture, not "8 lb of muscle."
  Captured the sources and coefficients in docs/measurement_notes.md.
- Kept the assumptions as named constants/dbt vars so the arithmetic is auditable.

**What I learned or got stuck on**
- Findings: fat reconciles (implied −11.2 vs observed −9.8, gap 1.4 lb); protein
  1.83 g/kg (in ACSM range, 16/30 days inside); recovery shows no overreaching
  signature (weak corrs, ~6.9 h sleep); regional volume did NOT track regional
  lean gain (Spearman −0.5, n=3) — arms got the most volume but the least lean
  change, consistent with the water confound swamping the training signal at this
  scale and window.
- Bug: marts defaulted to **views**, so an analysis query re-read a bronze file
  via a dbt-relative path and failed from the repo root. Fixed by materializing
  marts as **tables** (correct for a serving layer anyway). Also swapped a Polars
  `.corr` call for numpy.

**Next up**
- Phase 5: the Evidence.dev site reading from the marts, led by the
  reconciliation + uncertainty story, with every body-comp change shown with its
  band.
