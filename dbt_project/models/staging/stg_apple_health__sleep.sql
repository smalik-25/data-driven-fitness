-- Sleep analysis segments. value_str holds the HK sleep state; duration is
-- derived from start/end. "asleep*" states count toward time asleep.
select
    cast(start_date as date)                  as sleep_date,
    start_date,
    end_date,
    value_str                                 as sleep_state,
    date_diff('minute', start_date, end_date) as minutes,
    case when value_str like 'HKCategoryValueSleepAnalysisAsleep%'
         then 1 else 0 end                    as is_asleep
from {{ read_bronze('apple_health/sleep.parquet') }}
