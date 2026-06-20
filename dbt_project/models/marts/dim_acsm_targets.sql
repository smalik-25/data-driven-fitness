-- ACSM/ISSN reference ranges (protein, training volume). Grain: (metric, context).
select metric, context, low, high, unit, source
from {{ ref('stg_acsm__reference') }}
