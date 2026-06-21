select scan_date, fat_pct, lean_mass_lbs, fat_mass_lbs, total_mass_lbs
from silver_dexa where region = 'total' order by scan_date
