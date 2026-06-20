-- silver_daily_training_volume grain must be unique on (workout_date, region).
select workout_date, region, count(*) as n
from {{ ref('silver_daily_training_volume') }}
group by workout_date, region
having count(*) > 1
