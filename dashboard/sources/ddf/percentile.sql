select pct20_bf, pct40_bf, pct60_bf, pct80_bf
from dim_bodyfat_percentile
where sex = 'male' and 21 between age_min and age_max
