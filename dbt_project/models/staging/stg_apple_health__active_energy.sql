-- Active energy burned, per record (kcal). Grain: one Apple Health record.
select
    cast(start_date as date) as activity_date,
    value_num                as kcal,
    source_name
from {{ read_bronze('apple_health/active_energy.parquet') }}
where value_num is not null
