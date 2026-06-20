-- ACSM/ISSN reference ranges. Grain: one (metric, context).
select metric, context, low, high, unit, source
from {{ read_bronze('acsm/reference.parquet') }}
