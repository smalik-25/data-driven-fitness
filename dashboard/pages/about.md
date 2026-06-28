---
title: About
---

<div class="sm-eyebrow">§ 9.0 — ABOUT · WHY I BUILT THIS, AND WHY I CHECK THE INSTRUMENT FIRST</div>

_I build the plumbing that moves data quietly and correctly. This project is that plumbing pointed at my own body._

## ¶ 0 — The premise

I wanted a real data engineering project, the kind you have to earn: messy sources, a question I actually cared about, and an answer I couldn't just look up. Not another clean Kaggle CSV. So I instrumented myself. Two **DEXA scans** taken a month apart bracket a window where I logged basically everything: Apple Health (years of heart rate, energy, sleep, HRV), LoseIt food logs (calories and protein), and every set I lifted in Strong. Then I put population data next to mine, the NHANES-derived body-fat percentile chart and ACSM/ISSN nutrition guidance, so my numbers had something to be measured against.

The shape of the data is what makes it interesting. The outcomes are sparse but accurate: two precise body-composition snapshots. The inputs are dense and noisy: hundreds of thousands of behavioral records. A clean label at each end, a flood of explanatory signal in between. That's the shape of most real analytics problems, and the actual work is connecting the two without fooling yourself.

## ¶ 1 — Check the instrument before you trust the number

Between the two scans my reading moved by **−9.8 lb fat** and **+8.4 lb lean**, a textbook recomposition. The easy version of this project plots that, titles it "I gained 8 lb of muscle," and stops.

I didn't, because you can't build 8 lb of muscle in 30 days. Something other than muscle is sitting in that number. So the whole project hangs on one discipline: bound the uncertainty before you assert the result. DEXA counts every non-bone, non-fat gram as "lean tissue," water and blood and glycogen-bound fluid included. BodySpec's own experiment showed that a single gallon of water moved the lean reading by **7.4 lb**. And I started lifting right after the first scan, which adds real beginner muscle plus the water that newly trained muscle stores alongside glycogen. Pull those apart and the +8.4 lb reads as roughly **4 lb of plausible muscle and 4 lb of water**, sitting inside a ±3.4 lb precision band.

Refusing to call a measurement a fact until I've bounded its error is the part I care about most here. It's more of the actual skill than any single chart on the site.

## ¶ 2 — How I worked the question

A few habits show up on every page.

I triangulated. I didn't trust any one source on its own. The lean gain gets cross-examined three ways: does energy balance allow it, where do I sit against the population distribution, and how much of it could just be water (per the vendor's own hydration test). When two sources disagreed, like Apple Health reporting roughly twice the protein my food logs did, I treated that gap as a result worth reporting and then picked the source I trusted for a stated reason.

I stated the uncertainty. Every body-composition change on the site carries its band or its caveat. The DEXA window is 31 days but I only logged lifts for about 11 of them, and that mismatch is on the page, not buried in a footnote.

I decomposed instead of declaring. "Is the lean gain real?" isn't a yes/no. I split it into pieces I could each reason about, and the honest answer came out a mixture. The mixture is more useful than a verdict anyway.

## ¶ 3 — Why this stack

The stack is a current analytics-engineering spine, and I can defend each piece in a sentence.

- **Streaming ingestion in Python + Polars.** The Apple Health export is 328 MB, so I parse it with `lxml.iterparse` and clear each element as I go, which keeps memory flat. Bronze lands as partitioned Parquet.
- **DuckDB + dbt, medallion layout.** Bronze, then silver at a daily grain, then gold (a star schema plus the reconciliation marts). `fct_daily` carries an enforced contract; grain uniqueness and value ranges are tested.
- **DuckDB for dev, BigQuery for prod.** One dbt project, two targets. That split is about privacy and dev/prod parity, not scale. Raw data stays local; only de-identified marts reach the cloud and this public site.
- **Evidence.dev for serving.** SQL to a static site, so the dashboard reads straight from the marts and ships as a static bundle.
- **Airflow** to orchestrate ingest, silver, marts, analysis, and dashboard as one DAG.

## ¶ 4 — Built in public, kept private

This is health data, so the privacy handling is part of the engineering. Raw exports, the DEXA PDFs, anything identifying: all gitignored, none of it leaves my machine. Only derived, non-identifying aggregates get committed or published. The build itself is open, in a running [DEVLOG], conventional commits, and dbt docs, so you can audit the reasoning without ever seeing the raw data. Keeping data and code cleanly separated is most of what makes this safe to publish at all.

## ¶ 5 — What it shows

Streaming ingestion of large semi-structured data, dimensional modeling with contracts and tests, multi-source reconciliation, statistical honesty about measurement error, and clear communication of all of it. The headline isn't "I got lean." It's that I measured the instrument's noise floor, showed the signal partly sat inside it, and reconciled what was left against energy balance and population baselines.

<div class="sm-meta">↳ read next: [methods](/methods) · [data dictionary](/data-dictionary) · the [reconciliation](/reconciliation)</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
