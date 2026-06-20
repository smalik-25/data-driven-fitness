-- Logged bodyweight (lbs). Grain: one reading.
select
    cast(log_date as date) as log_date,
    weight_lbs
from {{ read_bronze('loseit/weights.parquet') }}
