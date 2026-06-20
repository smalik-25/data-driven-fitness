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
