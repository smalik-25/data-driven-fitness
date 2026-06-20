-- Heart rate variability (SDNN, ms), per record. Grain: one record.
select
    cast(start_date as date) as reading_date,
    value_num                as hrv_sdnn_ms
from {{ read_bronze('apple_health/hrv_sdnn.parquet') }}
where value_num is not null
