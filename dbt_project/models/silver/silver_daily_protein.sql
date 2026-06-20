-- Daily protein. Grain: one day.
-- protein_g is the canonical LoseIt food-log value; bodyweight is carried
-- forward from the most recent logged reading via an ASOF join (DuckDB).
-- NOTE: ASOF JOIN is a DuckDB feature; on BigQuery swap for a window/last_value
-- carry-forward. ah_protein_g is the Apple Health cross-check (inflated).
with food as (
    select log_date, protein_g, n_entries
    from {{ ref('stg_loseit__food_days') }}
),
weights as (
    select log_date, weight_lbs
    from {{ ref('stg_loseit__weights') }}
),
ah as (
    select log_date, sum(protein_g) as ah_protein_g
    from {{ ref('stg_apple_health__dietary_protein') }} group by 1
)
select
    f.log_date as day,
    f.protein_g,
    f.n_entries,
    w.weight_lbs,
    round(f.protein_g / (w.weight_lbs / 2.20462), 2) as protein_g_per_kg,
    ah.ah_protein_g
from food f
asof left join weights w on f.log_date >= w.log_date
left join ah on f.log_date = ah.log_date
