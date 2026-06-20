-- Per-region DEXA change between the two scans, with a measurement-uncertainty
-- band attached. Grain: one region.
-- A 95% band is propagated from per-scan CV assumptions (vars lean_cv / fat_cv);
-- is_*_resolvable flags whether the observed change exceeds the noise floor.
{% set lean_cv = var('lean_cv', 0.01) %}
{% set fat_cv  = var('fat_cv', 0.015) %}
with scans as (
    select region, scan_date, lean_mass_lbs, fat_mass_lbs, total_mass_lbs, fat_pct
    from {{ ref('silver_dexa') }}
),
t0 as (select * from scans where scan_date = (select min(scan_date) from scans)),
t1 as (select * from scans where scan_date = (select max(scan_date) from scans))
select
    t0.region,
    t0.lean_mass_lbs                                   as lean_t0,
    t1.lean_mass_lbs                                   as lean_t1,
    round(t1.lean_mass_lbs - t0.lean_mass_lbs, 2)      as lean_delta,
    round(1.96 * sqrt(
        pow({{ lean_cv }} * t0.lean_mass_lbs, 2) +
        pow({{ lean_cv }} * t1.lean_mass_lbs, 2)), 2)  as lean_delta_band95,
    abs(t1.lean_mass_lbs - t0.lean_mass_lbs) > 1.96 * sqrt(
        pow({{ lean_cv }} * t0.lean_mass_lbs, 2) +
        pow({{ lean_cv }} * t1.lean_mass_lbs, 2))      as lean_is_resolvable,
    t0.fat_mass_lbs                                    as fat_t0,
    t1.fat_mass_lbs                                    as fat_t1,
    round(t1.fat_mass_lbs - t0.fat_mass_lbs, 2)        as fat_delta,
    round(1.96 * sqrt(
        pow({{ fat_cv }} * t0.fat_mass_lbs, 2) +
        pow({{ fat_cv }} * t1.fat_mass_lbs, 2)), 2)    as fat_delta_band95,
    abs(t1.fat_mass_lbs - t0.fat_mass_lbs) > 1.96 * sqrt(
        pow({{ fat_cv }} * t0.fat_mass_lbs, 2) +
        pow({{ fat_cv }} * t1.fat_mass_lbs, 2))        as fat_is_resolvable
from t0 join t1 using (region)
