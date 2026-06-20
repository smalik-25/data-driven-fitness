-- Calendar spine over the data range. Grain: one day.
-- is_analysis_window flags the 2026-04-02..2026-05-02 DEXA bracket.
with bounds as (
    select min(day) as lo, max(day) as hi from {{ ref('silver_daily_energy') }}
),
spine as (
    select unnest(generate_series(lo::timestamp, hi::timestamp, interval '1 day'))::date as day
    from bounds
)
select
    day,
    extract(year from day)            as year,
    extract(month from day)           as month,
    strftime(day, '%A')               as day_of_week,
    (day between date '2026-04-02' and date '2026-05-02') as is_analysis_window
from spine
