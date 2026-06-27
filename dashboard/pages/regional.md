---
title: Regional Hypertrophy
---

<div class="sm-eyebrow">§ 2.0 — REGIONAL · DID THE MUSCLES I TRAINED MOST GAIN THE MOST?</div>

_The answer depends entirely on the metric — and the right metric flips the result._

```sql regional
select * from ddf.regional
```

<BarChart data={regional} x=region y=lean_pct_change title="Proportional lean growth by region (% of baseline)" yAxisTitle="lean Δ %" sort=false />

<BarChart data={regional} x=region y=volume_lbs title="In-window training volume by region (lbs)" sort=false />

<DataTable data={regional}>
  <Column id=region title="Region" />
  <Column id=volume_lbs title="Volume (lbs)" fmt='#,##0' />
  <Column id=working_sets title="Sets" />
  <Column id=lean_pct_change title="Lean Δ %" fmt='+0.0"%"' />
  <Column id=lean_pct_band95 title="± band %" fmt='0.0"%"' />
  <Column id=lean_delta_lbs title="Lean Δ (lbs)" fmt='+0.0' />
</DataTable>

## § 2.1 — Absolute lbs is the wrong metric; proportional growth is the right one

Hypertrophy should be measured **proportionally**. Arms are far smaller than the trunk, so they can't add as many absolute lbs — judging by lbs structurally penalizes them. As a share of their own baseline:

- **Arms** grew **+14.1%** — the most — on the most volume (46.5k lb).
- **Trunk** +7.8% at middling volume.
- **Legs** +5.4% — the least — on the least volume.

By **proportional** growth the ranking matches the training-volume ranking exactly (Spearman **+1.0**). By **absolute** lbs the trunk looks like the "winner" and the correlation is **−0.5** — the opposite conclusion, driven purely by region size. This is the lesson: *choose the metric that matches the question.*

### Variables on this page

- **Lean Δ %** — proportional lean change, `100 × lean_delta / lean_t0` (the hypertrophy metric).
- **± band %** — the 95% precision band expressed as a share of baseline (larger for small regions like arms).
- **Volume / Sets** — `Σ (weight × reps)` and working-set count in the window.
- **Lean Δ (lbs)** — the absolute change, kept only to show why it misleads.

### What this does and doesn't show

It shows that **once you use the right (proportional) metric, the most-trained region shows the most growth** — a clean training signal that the absolute view hid. It does **not** prove causation: n = 3 regions, ~11 logged days, and the hydration/glycogen confound still applies — and note glycogen loads *preferentially into trained muscles*, which would push proportional growth the same direction, so part of arms' +14% is likely trained-muscle water, not only fiber. Directional, not causal.

<div class="sm-callout">⚠ Caveat: Strong logging starts 2026-04-16 (~11 of 31 window days), n = 3, and proportional change amplifies measurement noise for small regions (arms' band is widest in % terms). Treat as directional.</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-callout { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #e0a838; border-left: 2px solid #e0a838; padding-left: .75rem; margin-top: 1rem; }
</style>
