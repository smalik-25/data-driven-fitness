-- Daily energy balance. Grain: one day.
-- TDEE = active + basal energy (Apple Health); intake = LoseIt food calories.
-- net_balance = intake - TDEE  (negative = deficit).
with active as (
    select activity_date as day, sum(kcal) as active_kcal
    from {{ ref('stg_apple_health__active_energy') }} group by 1
),
basal as (
    select activity_date as day, sum(kcal) as basal_kcal
    from {{ ref('stg_apple_health__basal_energy') }} group by 1
),
food as (
    select log_date as day, food_calories as intake_kcal
    from {{ ref('stg_loseit__food_days') }}
),
days as (
    select day from active
    union select day from basal
    union select day from food
)
select
    d.day,
    a.active_kcal,
    b.basal_kcal,
    (coalesce(a.active_kcal, 0) + coalesce(b.basal_kcal, 0)) as tdee_kcal,
    f.intake_kcal,
    f.intake_kcal - (coalesce(a.active_kcal, 0) + coalesce(b.basal_kcal, 0)) as net_balance_kcal
from days d
left join active a on d.day = a.day
left join basal  b on d.day = b.day
left join food   f on d.day = f.day
