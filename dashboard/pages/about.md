---
title: About
---

<div class="sm-eyebrow">§ 9.0 — ABOUT · RATIONALE, THOUGHT PROCESS, AND WHY THE INSTRUMENT COMES FIRST</div>

_I build the plumbing that moves data quietly and correctly. This project is that plumbing pointed at my own body._

## ¶ 0 — The premise

I wanted a data engineering project that was real — not a Kaggle CSV, but a pipeline I had to earn: messy sources, a genuine question, and a conclusion I couldn't look up. So I instrumented myself. Two **DEXA scans** exactly one month apart bracket a window in which I logged everything: Apple Health (years of heart rate, energy, sleep, HRV), LoseIt food logs (calories and protein), and every set I lifted in Strong. Against that I set **population data** — the NHANES-derived body-fat percentile chart and ACSM/ISSN nutrition guidance — so my numbers had a yardstick.

The shape of the data is what makes it interesting. The outcomes are **sparse but accurate** (two precise body-composition snapshots). The inputs are **dense but noisy** (hundreds of thousands of behavioral records). That asymmetry — a clean label at each end, a flood of explanatory signal in between — is the same shape as most real analytics problems. The craft is in connecting them honestly.

## ¶ 1 — The thesis: interrogate the instrument before you celebrate the number

Between the two scans my reading changed by **−9.8 lb fat** and **+8.4 lb lean** — a textbook body recomposition. The lazy version of this project plots that, titles it "I gained 8 lb of muscle," and stops.

I didn't, because **+8.4 lb of muscle in 30 days is not biologically possible.** Something other than muscle is in that number. So the spine of the whole project became a single discipline: *quantify the uncertainty before asserting the result.* DEXA classifies every non-bone, non-fat gram — water, blood, glycogen-bound fluid — as "lean tissue." BodySpec's own published experiment shows one gallon of water moves the lean reading by **7.4 lb**. I started training right after scan one, which adds real beginner muscle *and* training-onset glycogen loading (more water). Decomposed, the +8.4 lb is best read as **≤4.3 lb plausible newbie muscle plus ~4.1 lb glycogen/hydration water**, inside a ±3.4 lb precision band.

That move — refusing to call a measurement a fact until I've bounded its error — is the intellectual point of the project. It's also what separates an analyst from someone who colors in bar charts.

## ¶ 2 — How I think about a question like this

Three habits run through every page:

**Triangulation.** No single source is trusted alone. The lean gain is cross-examined by energy balance (does the math allow it?), by population data (where do I sit vs the distribution?), and by the vendor's own hydration experiment (how much could be water?). When sources disagree — Apple Health reported ~2× the protein my food logs did — I treat the disagreement as a finding, not a nuisance, and pick the more reliable source deliberately.

**Stated uncertainty.** Every body-composition change on this site is shown with its band or its caveat. The DEXA window is 31 days but I only logged lifts for ~11 of them; that mismatch is printed on the page, not hidden in a footnote.

**Decomposition over assertion.** Rather than answer "is the lean gain real?" yes/no, I split it into components I can each reason about. The honest answer is a mixture, and the mixture is more useful than a verdict.

## ¶ 3 — Why this architecture

The stack is a deliberate, current analytics-engineering spine, not a grab-bag:

- **Streaming ingestion in Python + Polars.** The Apple Health export is 328 MB; I parse it with `lxml.iterparse`, clearing each element so memory stays flat. Bronze lands as partitioned Parquet.
- **DuckDB + dbt, medallion layout.** Bronze → silver (daily grain) → gold (a star schema + reconciliation marts). `fct_daily` carries an *enforced contract*; grain uniqueness and value ranges are tested.
- **DuckDB for dev, BigQuery for prod.** One dbt project, two targets. This is a privacy and dev/prod-parity decision, not a scale one — private raw data stays local; only de-identified marts reach the cloud and this public site.
- **Evidence.dev** for the serving layer — SQL to static site, so the dashboard reads straight from the marts and deploys as a static bundle.
- **Airflow** (next) to orchestrate ingest → silver → marts → analysis → dashboard as one DAG.

Every choice has a one-line defense, which is the point: judgment is the deliverable.

## ¶ 4 — Built in public, built private

This is health data, so the privacy posture is part of the engineering. Raw exports, the DEXA PDFs, and anything identifying are gitignored and never leave my machine; only derived, non-identifying aggregates are committed or published. The build is logged in the open — a running [DEVLOG], conventional commits, dbt docs — so the reasoning is auditable even though the raw data is not. The discipline of separating data from code *is* the portfolio.

## ¶ 5 — What this demonstrates

Streaming ingestion of large semi-structured data; dimensional modeling with contracts and tests; multi-source reconciliation; statistical honesty about measurement error; and the communication of all of it. The headline finding isn't "I got lean" — it's that I **measured the instrument's noise floor, proved the signal partly sat inside it, and reconciled what remained against energy balance and population baselines.**

<div class="sm-meta">↳ read next: [methods](/methods) · [data dictionary](/data-dictionary) · the [reconciliation](/reconciliation)</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
