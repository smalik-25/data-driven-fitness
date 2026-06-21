select days_with_intake, cumulative_net_kcal, implied_fat_change_lbs,
       observed_fat_delta_lbs, fat_reconciliation_gap_lbs,
       lean_change_unexplained_by_energy_lbs, mean_protein_g_per_kg
from mart_recomp_reconciliation
