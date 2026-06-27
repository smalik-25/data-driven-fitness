select
    v.region,
    sum(v.volume_lbs)  as volume_lbs,
    sum(v.working_sets) as working_sets,
    c.lean_delta       as lean_delta_lbs,
    c.lean_delta_band95,
    c.lean_pct_change,
    c.lean_pct_band95
from silver_daily_training_volume v
join mart_dexa_change c on v.region = c.region
where v.workout_date between date '2026-04-02' and date '2026-05-02'
group by v.region, c.lean_delta, c.lean_delta_band95, c.lean_pct_change, c.lean_pct_band95
order by lean_pct_change desc
