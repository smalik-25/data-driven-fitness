with t as (select lean_delta, lean_delta_band95 from mart_dexa_change where region = 'total')
select
    lean_delta,
    lean_delta_band95,
    least(lean_delta, 4.29)                              as real_muscle_lbs,
    round(lean_delta - least(lean_delta, 4.29), 2)       as water_lbs,
    round((lean_delta - least(lean_delta, 4.29)) / 7.4, 2) as water_gallons,
    round(100 * (lean_delta - least(lean_delta, 4.29)) / lean_delta, 0) as water_pct
from t
