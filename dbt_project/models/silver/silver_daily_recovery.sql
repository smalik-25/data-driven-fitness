-- Daily recovery signals. Grain: one day.
-- Resting HR and HRV averaged per day; sleep summed from "asleep" segments.
with rhr as (
    select reading_date as day, avg(resting_hr_bpm) as resting_hr_bpm
    from {{ ref('stg_apple_health__resting_heart_rate') }} group by 1
),
hrv as (
    select reading_date as day, avg(hrv_sdnn_ms) as hrv_sdnn_ms
    from {{ ref('stg_apple_health__hrv') }} group by 1
),
sleep as (
    select sleep_date as day, sum(minutes) filter (where is_asleep = 1) as asleep_minutes
    from {{ ref('stg_apple_health__sleep') }} group by 1
),
days as (
    select day from rhr union select day from hrv union select day from sleep
)
select
    d.day,
    r.resting_hr_bpm,
    h.hrv_sdnn_ms,
    s.asleep_minutes,
    round(s.asleep_minutes / 60.0, 2) as sleep_hours
from days d
left join rhr r on d.day = r.day
left join hrv h on d.day = h.day
left join sleep s on d.day = s.day
