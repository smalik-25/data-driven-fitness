-- Canonical daily nutrition (calories + protein) from LoseIt food logs.
-- Grain: one day. Only Date/Calories/Protein are trusted (project rule).
select
    cast(log_date as date) as log_date,
    food_calories,
    protein_g,
    n_entries
from {{ read_bronze('loseit/food_days.parquet') }}
