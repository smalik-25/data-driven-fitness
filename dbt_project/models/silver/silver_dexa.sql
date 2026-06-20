-- The two DEXA scans, total + regional. Grain: one (scan_date, region).
-- This is the high-confidence outcome layer the whole project reconciles against.
select
    scan_date,
    region,
    fat_pct,
    total_mass_lbs,
    fat_mass_lbs,
    lean_mass_lbs,
    bmc_lbs
from {{ ref('stg_bodyspec__regional') }}
