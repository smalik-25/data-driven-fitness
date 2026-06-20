-- Resting heart rate, per record (bpm). Grain: one record.
select
    cast(start_date as date) as reading_date,
    value_num                as resting_hr_bpm
from {{ read_bronze('apple_health/resting_heart_rate.parquet') }}
where value_num is not null
