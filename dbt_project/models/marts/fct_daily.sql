-- The daily fact table. Grain: one calendar day across the data range.
-- Joins energy balance, protein, recovery, and training volume (pivoted to
-- arms/legs/trunk). Columns are cast to match the enforced dbt contract.
with spine as (
    select day, is_analysis_window from {{ ref('dim_date') }}
),
energy as (
    select day, active_kcal, basal_kcal, tdee_kcal, intake_kcal, net_balance_kcal
    from {{ ref('silver_daily_energy') }}
),
protein as (
    select day, protein_g, protein_g_per_kg, weight_lbs from {{ ref('silver_daily_protein') }}
),
recovery as (
    select day, resting_hr_bpm, hrv_sdnn_ms, sleep_hours from {{ ref('silver_daily_recovery') }}
),
volume as (
    select
        workout_date as day,
        sum(case when region = 'arms'  then volume_lbs end) as arms_volume_lbs,
        sum(case when region = 'legs'  then volume_lbs end) as legs_volume_lbs,
        sum(case when region = 'trunk' then volume_lbs end) as trunk_volume_lbs,
        sum(volume_lbs)   as total_volume_lbs,
        sum(working_sets) as total_working_sets
    from {{ ref('silver_daily_training_volume') }}
    group by 1
)
select
    spine.day::date                              as day,
    spine.is_analysis_window::boolean            as is_analysis_window,
    e.active_kcal::double                         as active_kcal,
    e.basal_kcal::double                          as basal_kcal,
    e.tdee_kcal::double                           as tdee_kcal,
    e.intake_kcal::double                         as intake_kcal,
    e.net_balance_kcal::double                    as net_balance_kcal,
    p.protein_g::double                           as protein_g,
    p.protein_g_per_kg::double                    as protein_g_per_kg,
    p.weight_lbs::double                          as weight_lbs,
    r.resting_hr_bpm::double                      as resting_hr_bpm,
    r.hrv_sdnn_ms::double                         as hrv_sdnn_ms,
    r.sleep_hours::double                         as sleep_hours,
    v.arms_volume_lbs::double                     as arms_volume_lbs,
    v.legs_volume_lbs::double                     as legs_volume_lbs,
    v.trunk_volume_lbs::double                    as trunk_volume_lbs,
    v.total_volume_lbs::double                    as total_volume_lbs,
    coalesce(v.total_working_sets, 0)::bigint     as total_working_sets
from spine
left join energy   e on spine.day = e.day
left join protein  p on spine.day = p.day
left join recovery r on spine.day = r.day
left join volume   v on spine.day = v.day
