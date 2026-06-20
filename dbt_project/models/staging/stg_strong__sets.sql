-- One row per logged set. Working-set volume = weight x reps. Warm-up sets
-- (set_order = 'W') are flagged so silver can exclude them from volume.
select
    cast(performed_at as date)                         as workout_date,
    performed_at,
    workout_name,
    exercise_name,
    set_order,
    weight_lbs,
    reps,
    rpe,
    (weight_lbs * reps)                                as volume_lbs,
    case when upper(set_order) = 'W' then 1 else 0 end as is_warmup
from {{ read_bronze('strong/sets.parquet') }}
