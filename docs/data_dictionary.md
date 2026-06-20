# Data Dictionary

Generated for Phase 2 (bronze → silver). One entry per model: grain, key columns,
and source. The shared join key across the daily models is the calendar **date**.

## Conventions

- **Units:** mass in lbs, energy in kcal, protein in grams, HRV in ms, sleep in
  minutes/hours. DEXA mass is lbs.
- **Analysis window:** 2026-04-02 → 2026-05-02 (the two DEXA scans). Sources are
  most reliable inside this window.
- **Bronze** (Parquet, `data/raw/`) is read only by staging models, via the
  `read_bronze()` macro. Silver and marts never touch raw files directly.

## Staging (views) — light cleaning, one model per bronze table

| Model | Grain | Notes |
|---|---|---|
| `stg_apple_health__active_energy` | one record | active kcal |
| `stg_apple_health__basal_energy` | one record | basal/resting kcal |
| `stg_apple_health__resting_heart_rate` | one record | bpm |
| `stg_apple_health__hrv` | one record | SDNN ms |
| `stg_apple_health__sleep` | one segment | `is_asleep` flags asleep states; `minutes` derived from start/end |
| `stg_apple_health__dietary_protein` | one record | **cross-check only** — inflated vs food logs |
| `stg_loseit__food_days` | one day | canonical calories + protein |
| `stg_loseit__weights` | one reading | bodyweight lbs |
| `stg_strong__sets` | one set | `volume_lbs = weight × reps`; `is_warmup` flags set_order='W' |
| `stg_bodyspec__regional` | (scan_date, region) | DEXA composition |
| `stg_acsm__reference` | (metric, context) | reference ranges |

## Silver (tables) — daily grain + outcome layer

| Model | Grain | Key columns | Built from |
|---|---|---|---|
| `silver_dexa` | (scan_date, region) | lean/fat/total mass, fat_pct, bmc | stg_bodyspec__regional |
| `silver_daily_energy` | one day | tdee_kcal, intake_kcal, **net_balance_kcal** | active + basal + food |
| `silver_daily_protein` | one day | protein_g, **protein_g_per_kg**, ah_protein_g (cross-check) | food_days + weights (ASOF) + AH protein |
| `silver_daily_recovery` | one day | resting_hr_bpm, hrv_sdnn_ms, sleep_hours | AH resting HR + HRV + sleep |
| `silver_daily_training_volume` | (workout_date, region) | volume_lbs, working_sets, total_reps | stg_strong__sets ⋈ dim_exercise |

## Seed

| Seed | Grain | Notes |
|---|---|---|
| `dim_exercise` | one exercise | exercise → region (arms/legs/trunk) + muscle_group. **Shoulders/delts → arms** (owner decision). All 38 logged exercises mapped. |

## Documented caveats (carried, not hidden)

- **DEXA delta is implausibly large** for 30 days (lean +8.4, fat −9.8 lb). The
  measurement-uncertainty analysis (Phase 4) treats this as the headline, not a
  fact to assert.
- **Strong logging starts 2026-04-16**, so only ~11 of 31 window days have logged
  lifts. Regional volume in the window is therefore partial — stated wherever
  training volume is used.
- **Apple Health protein (`ah_protein_g`) is ~2× inflated** vs the LoseIt food
  logs (≈260 vs ≈129 g/day in-window). Food logs are canonical; AH is a flag.
- **ASOF join** (bodyweight carry-forward in `silver_daily_protein`) is a DuckDB
  feature; on the BigQuery prod target swap for a `last_value` window.
