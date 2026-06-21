select day, total_volume_lbs, resting_hr_bpm, hrv_sdnn_ms, sleep_hours, protein_g_per_kg
from fct_daily
where is_analysis_window
order by day
