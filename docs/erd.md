# Schema / ERD

Layered warehouse: **bronze** (Parquet) → **silver** (daily grain) → **gold/marts**
(star schema + reconciliation marts). Bronze is read only by staging via the
`read_bronze()` macro; nothing downstream touches raw files.

## Gold star schema

```mermaid
erDiagram
    FCT_DAILY ||--o{ DIM_DATE : "day"
    SILVER_DAILY_TRAINING_VOLUME }o--|| DIM_EXERCISE : "exercise_name"
    SILVER_DAILY_TRAINING_VOLUME }o--|| DIM_REGION : "region"
    MART_DEXA_CHANGE }o--|| DIM_REGION : "region"
    MART_RECOMP_RECONCILIATION ||--|| MART_DEXA_CHANGE : "total region"
    FCT_DAILY }o--|| DIM_ACSM_TARGETS : "benchmark (protein g/kg)"
    SILVER_DEXA }o--|| DIM_BODYFAT_PERCENTILE : "benchmark (sex+age)"

    FCT_DAILY {
        date day PK
        bool is_analysis_window
        double tdee_kcal
        double intake_kcal
        double net_balance_kcal
        double protein_g_per_kg
        double arms_volume_lbs
        double legs_volume_lbs
        double trunk_volume_lbs
        bigint total_working_sets
    }
    MART_DEXA_CHANGE {
        string region PK
        double lean_delta
        double lean_delta_band95
        bool lean_is_resolvable
        double fat_delta
        double fat_delta_band95
        bool fat_is_resolvable
    }
    MART_RECOMP_RECONCILIATION {
        double cumulative_net_kcal
        double implied_fat_change_lbs
        double observed_fat_delta_lbs
        double fat_reconciliation_gap_lbs
        double lean_change_unexplained_by_energy_lbs
        double mean_protein_g_per_kg
    }
```

## Design notes

- **`fct_daily`** has an *enforced dbt contract* — grain (one day) and column
  types are guaranteed, so the marts and Phase-4 analysis can rely on them.
- **Benchmark dimensions are not time-joined.** `dim_acsm_targets` and
  `dim_bodyfat_percentile` are population yardsticks looked up by context /
  (sex, age), not joined on date. `dim_nhanes_bodycomp` is the raw-NHANES model,
  **disabled by default** (`var('enable_nhanes')`) since NHANES is network-loaded.
- **`mart_recomp_reconciliation`** is the single-row centerpiece: measured DEXA
  change vs energy-balance- and protein-implied change. Phase 4 builds on it.
- **Uncertainty bands** in `mart_dexa_change` come from per-scan CV vars
  (`lean_cv`, `fat_cv`); `kcal_per_lb` is also a var.
