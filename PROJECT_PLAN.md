# Data Driven Fitness — Project Plan & Cowork Playbook

**Goal:** End-to-end data engineering / analytics project that links my own body data (two DEXA scans, Apple Health, LoseIt, Strong) to population baselines (NHANES, ACSM) and answers five concrete physiology questions. Demonstrates streaming ingestion, dimensional modeling, dbt, orchestration, and a deployed analytics site. Built in public, with every phase documented through commits and a running devlog.

**Repo:** https://github.com/smalik-25/data-driven-fitness

**The headline finding to design around:** the two DEXA scans are exactly one month apart (4/2/2026 → 5/2/2026) and show −9.8 lb fat / +8.4 lb lean. That magnitude is biologically implausible in 30 days — it exceeds what energy balance can produce and reflects DEXA precision error and hydration variance. **Quantifying that measurement uncertainty, and showing the energy-balance math can't reconcile with the observed change, is the analytical spine of the project — not a bug to hide.** Every phase below serves that story.

**Stack:** Python + Polars · DuckDB (local dev) + BigQuery (cloud prod) · dbt-core · Apache Airflow · Evidence.dev · GitHub Actions. ML/forecasting is a deliberate Phase 2 extension, not part of this build.

**Warehouse architecture:** one dbt project, two targets. **DuckDB is the `dev` target** — local, fast, and the place all private raw data is processed (raw never leaves the machine). **BigQuery is the `prod` target** — only de-identified marts and the public reference layer (NHANES, ACSM) are materialized there, and the deployed Evidence.dev site reads from it. This is a deliberate dev/prod-parity and public-serving choice, *not* a scale decision — at this data volume DuckDB alone is plenty, and the README should say so plainly.

---

## 0. How to run this with Cowork

Cowork performs best when you describe the *outcome* you want for a session, not a literal step list — it plans its own steps. Use the phase prompts below as your starting message for each session. Paste them in as-is, then let Claude ask clarifying questions if it has them.

**Before Phase 1, set Folder Instructions** for this project folder (Settings > Cowork, or ask Claude in-session to save it as folder instructions). Use this:

```
This folder is "data-driven-fitness," a personal data engineering /
analytics portfolio project. Conventions to follow in every session:

- Python: type hints everywhere, dataclasses for structured records,
  docstrings on public functions, no bare except blocks. Prefer Polars
  over pandas for any reshaping over a few thousand rows.
- SQL/dbt: lowercase keywords, consistent style. Every dbt model gets a
  one-line comment at the top stating the question it answers or the
  grain it holds.
- Data honesty: this project's whole point is rigor about a noisy signal.
  Never state a body-composition change as fact without its measurement
  uncertainty. Always carry the DEXA precision caveat and the
  Strong-vs-DEXA window mismatch (Strong logging starts 4/16, the scans
  bracket 4/2-5/2) as documented assumptions, not silent ones.
- Git: Conventional Commits (feat:, fix:, docs:, refactor:, chore:,
  test:). One logical unit per commit, not an end-of-session dump.
- After any meaningful chunk of work, append a DEVLOG.md entry (template
  in the file) in first person — what was built AND why, not just what
  changed.
- Never push without showing me the diff and commit message first.
- Prefer readable, interview-explainable code over clever one-liners.
- Never commit raw health data: data/raw/ and the Apple Health export
  stay gitignored. Commit only derived, non-identifying aggregates.
```

This single block does most of the "build in public" work for you automatically going forward.

---

## 1. Repo structure

Kick off Phase 0 with this prompt:

```
This folder is already a git repo cloned from
github.com/smalik-25/data-driven-fitness, and it contains my raw source
data. Scaffold the project structure around the existing data WITHOUT
moving or committing any raw files. Create:

data-driven-fitness/
├── ingestion/
│   ├── __init__.py
│   ├── apple_health.py      # streaming XML -> partitioned parquet
│   ├── bodyspec.py          # API client + PDF regional-table parse
│   ├── loseit.py            # calorie/protein CSVs
│   ├── strong.py            # workout CSVs
│   ├── nhanes.py            # SAS XPORT (.XPT) downloader/loader
│   ├── acsm.py              # protein/training reference values
│   └── run_ingestion.py
├── warehouse/
│   └── ddf.duckdb           (gitignored)
├── dbt_project/
├── analysis/
│   ├── energy_balance.py
│   ├── regional_hypertrophy.py
│   ├── protein_lean.py
│   ├── recovery_load.py
│   └── measurement_uncertainty.py
├── airflow/                 # Airflow DAGs (dags/) + plugins
├── dashboard/               # Evidence.dev project
├── data/
│   └── raw/                 (gitignored — symlink or copy of sources)
├── docs/
│   ├── erd.md
│   └── data_dictionary.md
├── tests/
├── .github/workflows/
├── DEVLOG.md
├── README.md
├── Makefile
├── .gitignore               # MUST exclude all raw health data + *.duckdb
├── requirements.txt
└── pyproject.toml

Set up a Python virtual environment. Write a starter README.md with the
project description, the "measurement uncertainty is the story" framing,
the tech-stack table, and a "Progress" section with checkboxes for each
phase below (I'll give you the phase list separately). Create DEVLOG.md
with a template: Date / What I built / Why I made these decisions / What
I learned or got stuck on / Next up.

Before the first commit, verify .gitignore excludes export.xml, the
DEXA PDFs, all CSVs, data/raw/, and *.duckdb — confirm with `git status`
that no raw health data is staged. Then commit:
"chore: scaffold project structure"
```

---

## 2. Build-in-public system

Three mechanisms, set up once, that run for the rest of the project:

**DEVLOG.md** — append-only log, one entry per work session. Raw material for personal-site posts and for talking through the project in interviews. Ask Claude to write the entry at the end of each session before committing.

**README progress checklist** — a checkbox list of phases at the top of the README. Have Claude check off boxes and commit that as its own `docs:` commit when a phase wraps, so the commit history visibly tracks milestones.

**Commit message discipline** — Conventional Commits gives a clean, scannable history. When you link the repo from your personal site, the commit log itself becomes part of the portfolio narrative.

**Privacy note specific to this project:** this is health data. The build-in-public artifacts (DEVLOG, README, posts, dashboard) should show *methods, schema, code, and derived aggregates* — never the raw export or anything identifying. The `.gitignore` discipline from Phase 0 is part of the portfolio story, not a chore.

Optional: ask Claude to draft a short "Phase complete" post (300–500 words, your voice) at the end of each phase from that phase's DEVLOG entries. Save to `docs/posts/` so they're versioned alongside the code.

---

## 3. Phase-by-phase plan

### Phase 1 — Ingestion layer → bronze (Week 1)

```
Build the ingestion layer. Each source module follows the same pattern:
a dataclass for the record shape, a client/parser class with a public
generator method, real logging (not print), and per-record error
handling that doesn't crash the whole run.

Sources:
- apple_health.py: the export.xml is 328 MB — DO NOT load it into memory.
  Use lxml.iterparse / SAX, clearing elements as you go. Extract the
  record types we need (ActiveEnergyBurned, BasalEnergyBurned, StepCount,
  HeartRate, RestingHeartRate, HeartRateVariabilitySDNN, VO2Max,
  SleepAnalysis, Dietary* ) and Workout elements. Write partitioned
  Parquet to data/raw/apple_health/ by metric type.
- bodyspec.py: pull scan results via the Bodyspec API; also parse the two
  DEXA PDFs with pdfplumber to extract the Regional Assessment and
  Muscle Balance tables (arms/legs/trunk/android/gynoid lean+fat).
- loseit.py: daily-calorie-summary.csv + protein. Keep ONLY protein from
  macros (per project rules the other macros are unreliable).
- strong.py: strong_workouts.csv -> one row per set (exercise, weight,
  reps), parsed datetime.
- nhanes.py: download the relevant NHANES cycles, read the .XPT files
  with pandas.read_sas, keep DXA body-composition + demographics.
- acsm.py: encode ACSM/position-stand reference values (e.g. protein
  g/kg ranges for hypertrophy, training-volume guidance) as a small
  versioned reference table.

run_ingestion.py orchestrates all sources to Parquet/landing tables.
Keep ingestion fully decoupled from any modeling.

Tell me exactly what Bodyspec API credentials I need and where to put
them (.env, gitignored) before you write live calls; stub if needed.
Flag the data-quality facts up front in the DEVLOG: the implausible
DEXA delta, and that Strong starts 4/16 while the scan window is 4/2-5/2.

When it runs end to end, write the DEVLOG entry, update the README
checklist, show me the commit before pushing.
```

### Phase 2 — DuckDB warehouse + silver daily grain (Week 1–2)

```
Stand up DuckDB as the local warehouse (warehouse/ddf.duckdb, gitignored)
and set up dbt_project/ with dbt-core. Configure TWO targets in
profiles.yml: `dev` -> duckdb (default, used for all development), and
`prod` -> bigquery (used later for the public marts). Keep all SQL
warehouse-portable so the same models run against both; note any
dialect differences. The prod/BigQuery target stays unused until Phase 6
— just wire it now so the two-target architecture is real from the start.

Build the bronze->silver layers:
- bronze: external/seed models reading the Parquet + reference tables
  from Phase 1, one model per source, no logic.
- silver: cast types, standardize units (lbs, kcal, grams), clean nulls,
  and collapse the behavioral sources to a DAILY GRAIN. Produce
  stg_daily_energy (active+basal -> TDEE, intake, net balance),
  stg_daily_protein, stg_daily_recovery (resting HR, HRV, sleep),
  stg_strong_sets, and stg_dexa (the two scans, total + regional).

Map exercises to muscle groups: build dim_exercise that assigns each of
the 38 Strong exercises to a body region (arms / legs / trunk) so set
volume can be rolled up to the DEXA regions. Ask me to confirm any
ambiguous mappings.

Document the join key (date) and the grain of every model in a one-line
header comment. Write docs/data_dictionary.md.

DEVLOG entry, README checklist, commit for review before push.
```

### Phase 3 — dbt marts + NHANES/ACSM benchmarks + tests (Week 2–3)

```
Build the gold/marts layer as a star schema:

- fct_daily (grain: one day): net energy balance, TDEE, intake, protein
  g and g/kg, training volume by region (sets x reps x weight),
  sleep hours, HRV, resting HR.
- dim_date, dim_exercise (-> muscle_group), dim_region.
- Benchmark dimensions (NOT time-joined — used as population yardsticks):
  dim_nhanes_bodycomp keyed on age+sex giving DXA lean/fat percentiles,
  and dim_acsm_targets giving protein g/kg and volume reference ranges.
- mart_dexa_change: per-region lean/fat delta between the two scans,
  WITH the precision-error band attached to each delta.
- mart_recomp_reconciliation: observed mass change vs the change implied
  by cumulative net energy balance (3,500 kcal/lb for fat) and protein
  intake — the centerpiece reconciliation table.

dbt tests: not_null + unique on keys, relationships between fct and dims,
accepted_values on muscle_group and region. Add a dbt contract on
fct_daily. Write a short doc per mart stating the question it answers.

DEVLOG entry, README checklist, commit for review before push.
```

### Phase 4 — Analysis & statistics (Week 3–4)

This phase has no equivalent in the sneaker project — it's where the physiology questions get answered and where the rigor shows. Use the `statistical-analysis` skill.

```
Using the marts, answer the five questions in analysis/, each as a
documented script that writes results + a figure:

1. energy_balance.py — Did measured calorie balance predict the DEXA
   lean/fat change? Compute cumulative net balance over 4/2-5/2, convert
   to expected fat change at 3,500 kcal/lb, compare to observed. Expect
   a large gap — quantify it.
2. regional_hypertrophy.py — Which regions gained the most lean mass,
   and does that track Strong training volume by region (arms/legs/
   trunk)? Correlate regional volume with regional lean delta.
3. protein_lean.py — Rolling-window association between protein intake
   (g/kg) and lean change; benchmark intake against the ACSM range.
4. recovery_load.py — Did sleep, HRV, or resting HR move with training
   load? Look for overreaching signatures.
5. volume_efficiency.py — Lean mass gained per unit training volume, per
   muscle group.

THE CENTERPIECE — measurement_uncertainty.py: take DEXA precision error
(use BodySpec's stated accuracy / published DXA CV), propagate it onto
each regional and total delta, and show which observed changes are
inside the noise band vs genuinely resolvable. State plainly where the
signal is smaller than the instrument's noise floor.

Caveat every result with the Strong/DEXA window mismatch and n. Don't
overclaim. Verify the energy-balance and uncertainty math programmatically
(unit-test the conversions).

DEVLOG entry, README checklist, commit for review before push.
```

### Phase 5 — Evidence.dev analytics site (Week 4–5)

```
Build the public-facing analytics site in dashboard/ with Evidence.dev,
reading directly from the DuckDB marts. Match the visual style in
"Sam Malik Design System.md" in this folder. Pages:

1. Overview — body-composition change with uncertainty bands, my DEXA
   percentiles vs NHANES, headline KPIs.
2. The Reconciliation — energy-balance-implied vs DEXA-observed change,
   framed honestly as "the measured change exceeds what the inputs
   explain, and here's by how much."
3. Regional Hypertrophy — training volume by region next to regional
   lean change, with the window-mismatch caveat stated on the page.
4. Recovery — sleep / HRV / resting HR vs training load.

Keep the pages thin: SQL queries against marts + charts, no transformation
logic that belongs in dbt. Every chart that shows a body-comp change must
show its uncertainty band.

DEVLOG entry, README checklist, commit for review before push.
```

### Phase 6 — Orchestration, CI & polish (Week 5–6)

```
Wrap the pipeline in Apache Airflow (airflow/dags/): build one DAG that
chains the stages as tasks — ingest bronze parquet -> silver -> dbt marts
-> analysis outputs -> dashboard build — with explicit task dependencies
so the DAG graph reads as the pipeline lineage in the Airflow UI. Use the
TaskFlow API for the Python ingestion/analysis steps; run dbt either via
astronomer-cosmos (preferred — renders each dbt model as its own task) or
a BashOperator if you want to keep it simple. Run Airflow locally with the
official docker-compose (LocalExecutor is fine for this scale); document
the one-command spin-up in the README.

Add a Makefile (make ingest / make build / make analyze / make dashboard
/ make test) and a GitHub Actions workflow that runs dbt tests and the
analysis unit tests on every push to main. (CI runs against a small
synthetic/sample DuckDB, never real health data.)

Promote the de-identified marts and the public reference layer (NHANES,
ACSM) to the BigQuery `prod` target via `dbt build --target prod` (free
sandbox is fine). Point the deployed Evidence.dev site at BigQuery so the
live public dashboard reads from the cloud warehouse, while local DuckDB
stays private. Confirm NO identifying data reaches BigQuery — only
aggregates. Deploy the Evidence.dev site (Netlify or GitHub Pages) and get
me a live URL. Finalize README.md: description, architecture diagram
(mermaid),
tech-stack table, live demo link, how to run locally, and a
"Decisions & Tradeoffs" section pulling from DEVLOG — star schema vs
wide table, DuckDB dev target vs BigQuery prod target (and why this is a
privacy/dev-prod-parity choice, not a scale one), Airflow vs a lighter
scheduler for a single-machine pipeline, why measurement uncertainty is
front-and-center, why no ML yet.

Final DEVLOG entry summarizing the whole build. Mark all README checklist
items complete. Show me the commit before pushing.
```

---

## 4. Timeline

| Week | Phase | Deliverable |
|---|---|---|
| 1 | Ingestion | 6 source modules, streaming XML parse, bronze Parquet landing |
| 1–2 | Warehouse + silver | DuckDB up, dbt staging, daily-grain models, exercise→region map |
| 2–3 | Marts + benchmarks | Star-schema marts, NHANES/ACSM dims, reconciliation table, tests passing |
| 3–4 | Analysis | 5 questions answered + measurement-uncertainty centerpiece, math unit-tested |
| 4–5 | Dashboard | Evidence.dev site running locally against marts |
| 5–6 | Orchestrate + deploy | Airflow DAG, CI passing, live URL, README finalized |

Roughly 6 weeks at ~10 hrs/week, longer if you go deep on any phase. Each phase prompt is sized to one or two Cowork sessions.

---

## 5. Personal website integration

Once Phase 6 wraps, you'll have: a live Evidence.dev URL, a clean repo with a readable commit history and a visible Airflow DAG, a DEVLOG that's basically a build log, and (if you did the optional posts) 5–6 short writeups. That's enough for a single project page with: the live demo linked, a 2–3 paragraph summary led by the measurement-uncertainty finding, an architecture diagram, and links to specific commits or DEVLOG entries.

The differentiator to lead with on the page and in interviews: most personal fitness-data projects plot the numbers and declare victory. This one **interrogated the instrument, proved the headline change sat partly inside the noise floor, and reconciled it against energy balance and population baselines.** That's the analyst-vs-chart-maker distinction, and it's the thing worth putting at the top.

Ask Claude to draft that page copy once the repo is finalized — it'll have the full DEVLOG history to pull from.
```
