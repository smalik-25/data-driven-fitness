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

### Variables on this page

- **Volume (lbs)** — `Σ (weight × reps)` over working sets in the window, by region. Warm-ups excluded.
- **Sets** — count of working sets.
- **Lean Δ (lbs) / ± band** — regional lean change and its 95% precision band.
- **region** — each exercise mapped to a DEXA region; **shoulders/delts → arms** by design choice (see [data dictionary](/data-dictionary)).

### What this does and doesn't show

It shows that, at this scale, **training volume did not predict where lean was gained** (a negative rank correlation) — most consistent with regional water/glycogen noise dominating a small real signal. It does **not** disprove that training builds muscle; with n = 3 regions, ~11 logged days, and the hydration confound on every lean Δ, this is **directional, not causal**. The Spearman ρ here carries no statistical significance.

<div class="sm-callout">⚠ Caveat, stated loudly: Strong logging starts 2026-04-16, so only ~11 of 31 window days have logged lifts, and each lean Δ carries the hydration confound. Treat as directional, n = 3.</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-callout { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #e0a838; border-left: 2px solid #e0a838; padding-left: .75rem; margin-top: 1rem; }
</style>
