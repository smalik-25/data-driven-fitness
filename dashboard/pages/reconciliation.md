---
title: The Reconciliation
---

<div class="sm-eyebrow">§ 1.0 — RECONCILIATION · DOES THE MEASURED CHANGE MATCH THE INPUTS?</div>

_The honest test: can calories in/out and protein account for what the scan measured? Partly._

```sql recon
select * from ddf.reconciliation
```

<BigValue data={recon} value=cumulative_net_kcal title="Cumulative net energy (kcal)" fmt='#,##0' />
<BigValue data={recon} value=implied_fat_change_lbs title="Implied fat Δ (lbs)" fmt='+0.0' />
<BigValue data={recon} value=observed_fat_delta_lbs title="Observed fat Δ (lbs)" fmt='+0.0' />
<BigValue data={recon} value=fat_reconciliation_gap_lbs title="Gap (lbs)" fmt='+0.0' />

## § 1.1 — Fat reconciles

```sql fat_compare
select 'Implied by energy balance' as basis, implied_fat_change_lbs as lbs from ddf.reconciliation
union all
select 'Observed (DEXA)', observed_fat_delta_lbs from ddf.reconciliation
```

<BarChart data={fat_compare} x=basis y=lbs swapXY=true title="Fat change: predicted vs measured (lbs)" />

Over **<Value data={recon} column=days_with_intake/>** logged days the cumulative deficit implies **<Value data={recon} column=implied_fat_change_lbs/> lb** of fat; DEXA measured **<Value data={recon} column=observed_fat_delta_lbs/> lb** — a gap of only **<Value data={recon} column=fat_reconciliation_gap_lbs/> lb**. For fat, the energy-balance model holds up.

## § 1.2 — Lean does not

The same window shows **+<Value data={recon} column=lean_change_unexplained_by_energy_lbs/> lb lean**, which energy balance cannot produce — you cannot build 8 lb of muscle from a deficit. Protein was ample (**<Value data={recon} column=mean_protein_g_per_kg/> g/kg**, in the ACSM hypertrophy range), so some real newbie muscle is plausible — but the magnitude points to glycogen/hydration water, quantified on the [overview](/).

<div class="sm-meta">↳ the fat side is signal; the lean side is mostly the instrument. That distinction is the project.</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
