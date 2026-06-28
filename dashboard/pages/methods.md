---
title: Methods
---

<div class="sm-eyebrow">§ 8.0 — METHODS · THE STATS AND THE CODE, IN DETAIL</div>

_Every number on this site is reproducible from raw files, by code that's tested. Here's how I did it, and why I made each call._

## § 8.1 — Ingestion

**Apple Health (328 MB XML).** I parse it with `lxml.iterparse` on end-events, clearing each element and its processed siblings as I go, so the parser never holds more than a fragment of the tree in memory. A naive DOM load would allocate the whole 328 MB. The streaming parse runs in about 18 s at ~0.5 GB peak and keeps only the ~376 k records matching a whitelist of metric types. Each metric is written as its own Parquet file (the **bronze** layer).

**LoseIt.** Food logs read with Polars and aggregated to a daily grain (`group_by(date) → sum`). I trust only `Date`, `Calories`, and `Protein`; the other macros are dropped by rule. Soft-deleted rows are filtered on the `Deleted` flag.

**Strong.** One row per set, with working-set volume as `weight × reps`. Warm-up sets (`set_order = 'W'`) are flagged so they stay out of the volume totals.

**BodySpec DEXA.** Two paths to the same shape: a `pdfplumber` regex parse of the report tables (the verified default, no credentials needed), and a Bearer-JWT API client built from the OpenAPI spec that lists results, fetches `/dexa/composition`, converts kg to lb, and sums left/right limbs into combined regions.

**NHANES.** SAS XPORT (`.XPT`) files read with `pandas.read_sas`, kept as a benchmark dimension. It's network-bound, so it's off by default in offline builds.

## § 8.2 — Modeling (dbt on DuckDB)

A **medallion** layout. **Bronze** is raw Parquet, touched only by staging. **Silver** casts types, standardizes units (lbs, kcal, grams), and collapses each behavioral source to a **daily grain**. That grain is the natural join key, since almost every input is one row per day and the DEXA outcomes are timestamped points. **Gold** is a star schema: `fct_daily` (one day per row) plus dimensions, and the two reconciliation marts.

Quality is enforced rather than assumed. `fct_daily` carries a **dbt contract** that guarantees column types, and tests cover not-null and unique keys, accepted-value sets, and grain uniqueness (that last one via zero-dependency singular tests, so the suite runs offline). Bodyweight is carried forward to each day with a DuckDB **ASOF join** against the sparse weight log.

## § 8.3 — Energy balance

**TDEE** (total daily energy expenditure) is `active_energy + basal_energy` from Apple Health. **Net balance** is `intake − TDEE`, where negative means a deficit. Over the window I sum net balance and convert to fat mass with the classic approximation:

```
implied_fat_change_lbs = cumulative_net_kcal / 3500
```

The **3,500 kcal/lb** figure is the energy density of stored body fat, and it's an approximation. Real tissue change mixes fat, water, and lean, and metabolism adapts so TDEE drifts over time. I'm using it as a deliberate first-order check. The result (implied −11.2 lb against observed −9.8 lb, a 1.4 lb gap) is close enough to say the fat side reconciles, with the caveat that this is a model and not a hard law.

## § 8.4 — The measurement-uncertainty decomposition (centerpiece)

I split the observed lean change into three components I can each defend.

**1 · Random precision.** Two independent scans, each with a coefficient of variation `cv ≈ 1%` for lean tissue. Independent errors add in quadrature, so the 95% band on the *difference* is:

```
band95 = 1.96 × sqrt( (cv·lean_t0)² + (cv·lean_t1)² )
```

For lean 119.5 → 127.9 lb that's ±3.43 lb. The observed +8.4 lb clears it, so the change is **resolvable against random noise**. That only rules out one source of error, though.

**2 · Plausible real (newbie) muscle.** I started training at scan one, so genuine beginner muscle gain is on the table. Untrained lifters can credibly add ~0.5–1.0 lb/week early on, so I cap the real component at **1 lb/week × (30/7) ≈ 4.3 lb** as a generous ceiling.

**3 · Glycogen / hydration water.** Whatever's left. DEXA reads water as lean, and BodySpec's own experiment pins the coefficient at **7.4 lb of lean per gallon** of water:

```
real_muscle = min(lean_delta, 4.29)
water_lbs   = lean_delta − real_muscle          # ≈ 4.11 lb
water_gallons = water_lbs / 7.4                  # ≈ 0.56 gal
```

A little over half a gallon of net water retention covers the non-muscle part, which is entirely plausible from training-onset glycogen loading plus a hydration difference between the two scan days. So the conclusion lands as a mixture, stated with its assumptions, rather than a clean verdict.

## § 8.5 — Correlations and their limits

For regional hypertrophy I use **proportional** lean change (`100 × lean_delta / lean_t0`) instead of absolute lbs. Absolute change structurally favors big muscle groups, so a small group like the arms can't add as many lbs even when it grows more as a share of itself. The link to training volume is a **Spearman rank correlation** across three regions, and the metric choice decides the answer: proportional change ranks +1.0 with volume (the most-trained region grew most), while absolute lbs ranks −0.5 (the reverse). At **n = 3** both are illustrative, good enough to show rank agreement or reversal but carrying no real significance. The recovery page reports Pearson correlations between training load and resting HR, HRV, and sleep over 31 days; with lifts logged for only ~11 of them, I read those as directional, not causal. I report the numbers and label their limits plainly.

## § 8.6 — Programming practice

Type hints throughout, dataclasses for record shapes, generators for streaming, and per-record error handling (no bare excepts) so one bad row never kills a run. Logging, not print statements. The arithmetic the conclusions actually rest on, the 3,500 kcal/lb conversion, the quadrature band, the gallon-equivalent, and the newbie bound, is covered by `pytest` so a refactor can't quietly change a result. `ruff` lints the code, and GitHub Actions runs the tests on every push against a synthetic sample, never real data. dbt is the single source of truth for transformations, and nothing downstream re-reads raw files.

<div class="sm-meta">↳ definitions for every variable: [data dictionary](/data-dictionary) · narrative: [about](/about)</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
