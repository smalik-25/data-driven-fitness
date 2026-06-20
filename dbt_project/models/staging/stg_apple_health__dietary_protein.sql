-- Apple Health protein (g). Inflated vs LoseIt food logs; kept only as a
-- cross-check, NOT the canonical protein source. Grain: one record.
select
    cast(start_date as date) as log_date,
    value_num                as protein_g
from {{ read_bronze('apple_health/dietary_protein.parquet') }}
where value_num is not null
