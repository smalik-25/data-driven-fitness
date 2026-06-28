---
title: Regional Hypertrophy
---

<div class="sm-eyebrow">§ 2.0 — REGIONAL · DID THE MUSCLES I TRAINED MOST GAIN THE MOST?</div>

_The answer depends entirely on the metric, and the right one flips the result._

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

Hypertrophy is better measured **proportionally**. Arms are much smaller than the trunk, so they can't add as many absolute pounds, and grading by pounds quietly penalizes them. As a share of each region's own baseline:

- **Arms** grew the most, **+14.1%**, on the most volume (46.5k lb).
- **Trunk** grew **+7.8%** at middling volume.
- **Legs** grew the least, **+5.4%**, on the least volume.

Ranked by proportional growth, the order matches the training-volume order exactly (Spearman **+1.0**). Ranked by absolute pounds, the trunk looks like the winner and the correlation flips to **−0.5**, purely because the trunk is bigger. The takeaway is to pick the metric that matches the question.

### Variables on this page

- **Lean Δ %** — proportional lean change, `100 × lean_delta / lean_t0` (the hypertrophy metric).
- **± band %** — the 95% precision band expressed as a share of baseline (larger for small regions like arms).
- **Volume / Sets** — `Σ (weight × reps)` and working-set count in the window.
- **Lean Δ (lbs)** — the absolute change, kept only to show why it misleads.

### What this does and doesn't show

With the right (proportional) metric, the most-trained region also grew the most, a clean training signal the absolute view hid. It doesn't prove causation. There are only three regions and about 11 logged days, and the hydration/glycogen confound still applies. Glycogen also loads *preferentially into trained muscles*, which pushes proportional growth in the same direction, so part of arms' +14% is probably trained-muscle water rather than fiber. Read it as directional.

<div class="sm-callout">⚠ Caveat: Strong logging starts 2026-04-16 (~11 of 31 window days), n = 3, and proportional change amplifies measurement noise for small regions (arms' band is widest in % terms). Treat as directional.</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-callout { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #e0a838; border-left: 2px solid #e0a838; padding-left: .75rem; margin-top: 1rem; }
</style>
