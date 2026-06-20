-- Daily training volume by DEXA region. Grain: one (workout_date, region).
-- Volume = sum(weight x reps) over working sets (warm-ups excluded), with each
-- exercise mapped to a body region via the dim_exercise seed.
with sets as (
    select * from {{ ref('stg_strong__sets') }} where is_warmup = 0
),
mapped as (
    select
        s.workout_date,
        e.region,
        e.muscle_group,
        s.volume_lbs,
        s.reps
    from sets s
    left join {{ ref('dim_exercise') }} e using (exercise_name)
)
select
    workout_date,
    region,
    sum(volume_lbs)  as volume_lbs,
    count(*)         as working_sets,
    sum(reps)        as total_reps
from mapped
group by 1, 2
