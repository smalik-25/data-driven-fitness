---
title: Recovery
---

<div class="sm-eyebrow">§ 3.0 — RECOVERY · DID TRAINING LOAD MOVE SLEEP, HRV, RESTING HR?</div>

_Looking for an overreaching signature: rising resting HR, falling HRV, falling sleep as load ramps._

```sql recovery
select * from ddf.recovery
```

<LineChart data={recovery} x=day y=total_volume_lbs title="Training volume across the window (lbs)" />

<LineChart data={recovery} x=day y={["resting_hr_bpm","hrv_sdnn_ms"]} title="Resting HR (bpm) & HRV SDNN (ms)" />

<LineChart data={recovery} x=day y=sleep_hours title="Sleep (hours)" yAxisTitle="hours" />

## § 3.1 — No overreaching signature

Across the window the correlations between training load and recovery signals are weak in every direction — resting HR barely moves, HRV drifts slightly down, sleep is flat at roughly 6.9 h. Nothing here looks like accumulating fatigue, though the window is short and lifts are only logged from 2026-04-16.

<DataTable data={recovery}>
  <Column id=day title="Day" />
  <Column id=total_volume_lbs title="Volume (lbs)" fmt='#,##0' />
  <Column id=resting_hr_bpm title="Resting HR" fmt='0.0' />
  <Column id=hrv_sdnn_ms title="HRV (ms)" fmt='0.0' />
  <Column id=sleep_hours title="Sleep (h)" fmt='0.0' />
</DataTable>

<div class="sm-meta">↳ short window · correlations illustrative, not causal</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
