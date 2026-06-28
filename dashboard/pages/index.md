---
title: Data Driven Fitness
---

<div class="sm-eyebrow">§ 0.0 — OVERVIEW · ONE MONTH BETWEEN TWO DEXA SCANS</div>

_Most fitness dashboards plot the number and declare victory. This one interrogates the instrument first._

```sql totals
select * from ddf.dexa_totals
```

```sql change
select * from ddf.dexa_change where region = 'total'
```

<BigValue
  data={totals}
  value=fat_pct
  title="Body fat %"
  comparison=fat_pct
  comparisonTitle="start 21.7%"
  fmt='0.0"%"'
/>

<BigValue data={change} value=lean_delta title="Lean Δ (lbs)" fmt='+0.0' />
<BigValue data={change} value=fat_delta title="Fat Δ (lbs)" fmt='+0.0' />

Body fat fell **21.7% → 15.7%** in 30 days. That puts me below the 20th-percentile body-fat cut for men 20–29, leaner than about 80% of the age group (`dim_bodyfat_percentile`, NHANES-derived). The fat loss is real, and it reconciles with energy balance. The **lean "gain" is the part I'd be careful with.**

## § 0.1 — The lean gain, decomposed

```sql unc
select * from ddf.uncertainty
```

```sql buckets
select * from ddf.uncertainty_buckets
```

<BarChart data={buckets} x=bar y=lbs series=component type=stacked swapXY=true title="The +8.4 lb 'lean gain' is not 8.4 lb of muscle" />

The reading shows **+<Value data={unc} column=lean_delta/> lb lean**. At most **<Value data={unc} column=real_muscle_lbs/> lb** of that is plausible newbie muscle in a month. The rest, **<Value data={unc} column=water_lbs/> lb (<Value data={unc} column=water_pct/>%)**, about **<Value data={unc} column=water_gallons/> gallons of water**, fits training-onset glycogen loading plus a scan-day hydration difference. DEXA counts all non-bone, non-fat mass as "lean," water included.

<div class="sm-meta">↳ method · docs/measurement_notes.md · BodySpec gallon-of-water experiment: 7.4 lb lean per gallon</div>

### Variables on this page

- **Body fat %** — fat mass as a share of total mass, measured by DEXA.
- **Lean Δ / Fat Δ** — change in lean / fat mass between the two scans, in lbs.
- **real muscle / water** — the decomposition: `min(lean Δ, 4.3 lb)` is the plausible newbie-muscle ceiling; the remainder is expressed as water at BodySpec's 7.4 lb-per-gallon coefficient.

### What this does and doesn't show

It shows the **fat loss is real** and that the **lean gain is roughly half non-muscle water**. It doesn't claim an exact muscle figure: 4.3 lb is an upper bound, not a point estimate. And "resolvable" only means the change beats *random* precision noise, which isn't the same as it being muscle. Hydration is a separate and larger systematic effect. Definitions live in the [data dictionary](/data-dictionary); the derivation is in [methods](/methods).

## § 0.2 — Read on

- [The reconciliation](/reconciliation): what energy balance can and can't explain.
- [Regional hypertrophy](/regional): did the muscles I trained most gain the most?
- [Recovery](/recovery): did training load move sleep, HRV, or resting HR?

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
