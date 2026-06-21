---
title: Regional Hypertrophy
---

<div class="sm-eyebrow">§ 2.0 — REGIONAL · DID THE MUSCLES I TRAINED MOST GAIN THE MOST?</div>

_The cleanest causal story in the project — and it doesn't hold, for an instructive reason._

```sql regional
select * from ddf.regional
```

<BarChart data={regional} x=region y=volume_lbs title="In-window training volume by region (lbs)" />

<BarChart data={regional} x=region y=lean_delta_lbs title="Regional lean change (lbs)" yAxisTitle="lean Δ (lbs)" />

<DataTable data={regional}>
  <Column id=region title="Region" />
  <Column id=volume_lbs title="Volume (lbs)" fmt='#,##0' />
  <Column id=working_sets title="Sets" />
  <Column id=lean_delta_lbs title="Lean Δ (lbs)" fmt='+0.0' />
  <Column id=lean_delta_band95 title="± band 95%" fmt='0.00' />
</DataTable>

## § 2.1 — Volume did not predict lean change

**Arms** took the most volume (46.5k lb, 97 sets) but gained the **least** lean (+1.9 lb). **Trunk** gained the most (+4.2 lb) at middling volume. The rank correlation is actually negative.

That isn't a null result — it's what you'd expect when the lean signal is dominated by water rather than training: regional glycogen/hydration noise swamps a real but small hypertrophy signal over a short window.

<div class="sm-callout">⚠ Caveat, stated loudly: Strong logging starts 2026-04-16, so only ~11 of 31 window days have logged lifts, and each lean Δ carries the hydration confound. Treat as directional, n = 3.</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-callout { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #e0a838; border-left: 2px solid #e0a838; padding-left: .75rem; margin-top: 1rem; }
</style>
