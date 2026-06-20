-- THE CENTERPIECE. One row reconciling the measured DEXA change against what the
-- inputs (energy balance + protein) can explain over the analysis window.
-- implied fat change = cumulative net energy balance / 3500 kcal-per-lb.
-- The lean gain is the part energy balance cannot account for.
{% set kcal_per_lb = var('kcal_per_lb', 3500) %}
with window_energy as (
    select
        sum(net_balance_kcal) as cum_net_kcal,
        count(*)              as days_with_intake
    from {{ ref('fct_daily') }}
    where is_analysis_window and intake_kcal is not null
),
window_protein as (
    select avg(protein_g_per_kg) as mean_protein_g_per_kg
    from {{ ref('fct_daily') }}
    where is_analysis_window and protein_g is not null
),
dexa as (
    select
        fat_delta  as observed_fat_delta_lbs,
        lean_delta as observed_lean_delta_lbs
    from {{ ref('mart_dexa_change') }}
    where region = 'total'
)
select
    e.days_with_intake,
    round(e.cum_net_kcal)                                  as cumulative_net_kcal,
    round(e.cum_net_kcal / {{ kcal_per_lb }}, 2)           as implied_fat_change_lbs,
    d.observed_fat_delta_lbs,
    round(d.observed_fat_delta_lbs
          - (e.cum_net_kcal / {{ kcal_per_lb }}), 2)       as fat_reconciliation_gap_lbs,
    d.observed_lean_delta_lbs                              as lean_change_unexplained_by_energy_lbs,
    round(p.mean_protein_g_per_kg, 2)                      as mean_protein_g_per_kg
from window_energy e
cross join window_protein p
cross join dexa d
