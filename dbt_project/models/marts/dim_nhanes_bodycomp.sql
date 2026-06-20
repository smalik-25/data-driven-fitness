-- Raw NHANES DXA body composition (national reference sample).
-- DISABLED by default: NHANES is network-downloaded and absent in offline
-- builds/CI. After running `python -m ingestion.nhanes --with-nhanes`, enable
-- with: dbt build --vars 'enable_nhanes: true'.
{{ config(enabled = var('enable_nhanes', false)) }}
select
    respondent_id,
    sex,
    age_years,
    total_body_fat_pct,
    total_lean_g,
    total_fat_g
from {{ read_bronze('nhanes/bodycomp.parquet') }}
