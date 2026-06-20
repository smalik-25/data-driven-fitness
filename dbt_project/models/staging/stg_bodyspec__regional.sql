-- DEXA regional composition. Grain: one (scan_date, region).
select
    cast(scan_date as date) as scan_date,
    lower(region)           as region,
    fat_pct,
    total_mass_lbs,
    fat_mass_lbs,
    lean_mass_lbs,
    bmc_lbs
from {{ read_bronze('bodyspec/regional.parquet') }}
