---
title: Methods
---

<div class="sm-eyebrow">§ 8.0 — METHODS · STATISTICAL AND PROGRAMMING TECHNIQUE, IN DETAIL</div>

_Every number on this site is reproducible from raw files by code that is tested. Here is how, and why each choice was made._

## § 8.1 — Ingestion

**Apple Health (328 MB XML).** Parsed with `lxml.iterparse` over end-events, clearing each element and its processed siblings after reading so the parser never holds more than a fragment of the tree in memory. A naive DOM load would allocate the whole 328 MB; the streaming parse runs in ~18 s at ~0.5 GB peak, keeping only the ~376 k records that match a whitelist of metric types. Each metric is written as its own Parquet file (the **bronze** layer).

**LoseIt.** Food logs are read with Polars and aggregated to a daily grain (`group_by(date) → sum`). Only `Date`, `Calories`, and `Protein` are trusted; the other macros are discarded by rule. Soft-deleted rows are filtered on the `Deleted` flag.

**Strong.** One row per set; working-set volume is computed as `weight × reps`. Warm-up sets (`set_order = 'W'`) are flagged so they can be excluded from volume.

**BodySpec DEXA.** Two paths to identical shape: a `pdfplumber` regex parse of the report tables (the verified default, no credentials), and a Bearer-JWT API client built from the OpenAPI spec (lists results, fetches `/dexa/composition`, converts kg→lb, sums left/right limbs into combined regions).

**NHANES.** Downloaded SAS XPORT (`.XPT`) files read with `pandas.read_sas`; kept as a benchmark dimension. Network-bound, so disabled by default in offline builds.

## § 8.2 — Modeling (dbt on DuckDB)

A **medallion** architecture. **Bronze** is raw Parquet, touched only by staging. **Silver** casts types, standardizes units (lbs, kcal, grams), and collapses each behavioral source to a **daily grain** — the natural join key, since almost every input is one-row-per-day and the DEXA outcomes are timestamped points. **Gold** is a star schema: `fct_daily` (one day per row) plus dimensions, and two reconciliation marts.

Quality is enforced, not hoped for: `fct_daily` carries a **dbt contract** (column types guaranteed), and tests cover not-null/unique keys, accepted-value sets, and grain uniqueness (the last via zero-dependency singular tests, so the suite runs offline). Bodyweight is carried forward to each day with a DuckDB **ASOF join** against the sparse weight log.

## § 8.3 — Energy balance

**TDEE** (total daily energy expenditure) = `active_energy + basal_energy` from Apple Health. **Net balance** = `intake − TDEE`; negative is a deficit. Over the window I sum net balance and convert to fat mass with the classic approximation:

```
implied_fat_change_lbs = cumulative_net_kcal / 3500
```

The **3,500 kcal/lb** figure is the energy density of stored body fat and is an *approximation* — real tissue change mixes fat, water, and lean, and adaptive metabolism shifts TDEE over time. I use it deliberately as a first-order check, and the result (implied −11.2 lb vs observed −9.8 lb, a 1.4 lb gap) is close enough to say the fat side reconciles, while being honest that it's a model, not a law.

## § 8.4 — The measurement-uncertainty decomposition (centerpiece)

The observed lean change is split into three components I can each defend.

**1 · Random precision.** Two independent scans, each with a coefficient of variation `cv ≈ 1%` for lean tissue. Independent errors add in quadrature, so the 95% band on the *difference* is:

```
band95 = 1.96 × sqrt( (cv·lean_t0)² + (cv·lean_t1)² )
```

For lean 119.5 → 127.9 lb this is ±3.43 lb. The observed +8.4 lb exceeds it, so the change is **resolvable against random noise** — but that only rules out one error source.

**2 · Plausible real (newbie) muscle.** I started training at scan one, so genuine beginner muscle gain is in play. Untrained lifters credibly add ~0.5–1.0 lb/week early; I cap the real component at **1 lb/week × (30/7) ≈ 4.3 lb** as a generous upper bound.

**3 · Glycogen / hydration water.** The remainder. DEXA reads water as lean, and BodySpec's own experiment fixes the coefficient: **7.4 lb lean per gallon** of water. So:

```
real_muscle = min(lean_delta, 4.29)
water_lbs   = lean_delta − real_muscle          # ≈ 4.11 lb
water_gallons = water_lbs / 7.4                  # ≈ 0.56 gal
```

A little over half a gallon of net water retention — entirely plausible from training-onset glycogen loading plus scan-day hydration differences — accounts for the non-muscle part. The conclusion is a *mixture*, stated with its assumptions, not a verdict.

## § 8.5 — Correlations and their limits

Regional hypertrophy uses **proportional** lean change (`100 × lean_delta / lean_t0`), not absolute lbs — absolute change structurally favors large muscle groups, so a small group like the arms can't add as many lbs even if it grows more as a share of itself. The association with training volume is a **Spearman rank correlation** across three regions. The metric choice matters: proportional change ranks +1.0 with volume (most-trained region grew most), while absolute lbs ranks −0.5 (the opposite). With **n = 3** both are illustrative — they show rank agreement or reversal but carry no significance. The recovery page reports Pearson correlations between training load and resting HR / HRV / sleep over 31 days; with lifts logged for only ~11 of them, these too are read as directional, not causal. I report the numbers and label them rather than dressing them up.

## § 8.6 — Programming practice

Type hints throughout; dataclasses for record shapes; generators for streaming; no bare excepts (per-record error handling so one bad row never kills a run); logging rather than prints. The arithmetic that the conclusions rest on — the 3,500 kcal/lb conversion, the quadrature band, the gallon-equivalent, the newbie bound — is covered by `pytest` unit tests, so a refactor can't silently change a result. `ruff` lints the codebase; GitHub Actions runs the tests on every push against a synthetic sample, never real data. dbt is the single source of truth for transformations; nothing downstream re-reads raw files.

<div class="sm-meta">↳ definitions for every variable: [data dictionary](/data-dictionary) · narrative: [about](/about)</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
