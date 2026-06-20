-- Basal (resting) energy burned, per record (kcal). Grain: one record.
select
    cast(start_date as date) as activity_date,
    value_num                as kcal,
    source_name
from {{ read_bronze('apple_health/basal_energy.parquet') }}
where value_num is not null
