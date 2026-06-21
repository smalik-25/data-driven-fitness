# Measurement notes — DEXA uncertainty & the lean-mass interpretation

Reference material grounding the Phase 4 measurement-uncertainty analysis. Sourced
from BodySpec's own published blog experiments.

## 1. Hydration sensitivity (the key coefficient)

BodySpec scanned a subject before and after drinking **one gallon** of water
(taken slowly over ~1 hour):

| Metric | Before | After | Δ (per gallon) |
|---|---|---|---|
| Total mass (lbs) | 179.6 | 186.0 | **+6.4** |
| Body fat % | 14.6 | 13.6 | **−1.0** |
| Fat tissue (lbs) | 26.2 | 25.2 | **−1.0** |
| **Lean tissue (lbs)** | 145.5 | 152.9 | **+7.4** |
| Bone (lbs) | 7.9 | 7.9 | 0.0 |

Why: DEXA classifies **all non-bone, non-fat matter — including water, blood, and
glycogen-bound fluid — as "lean tissue."** So added body water reads directly as
"lean mass gain."

Derived coefficients used in the analysis:

- `LEAN_LB_PER_GALLON = 7.4`  (lean reading change per gallon of water)
- `FAT_LB_PER_GALLON  = -1.0`
- `BODYFAT_PCT_PER_GALLON = -1.0`
- 1 gallon ≈ 8.345 lb of water ≈ 16 cups → ~0.5–1 cup is negligible.

**Implication for this project:** the observed **+8.4 lb lean** change is ≈ the
lean swing of a single gallon of water (+7.4 lb). A modest, entirely plausible
hydration / glycogen difference between the two scan days could therefore explain
most of the apparent "muscle gain." This is the heart of the measurement-
uncertainty centerpiece: the lean delta clears the *random* precision noise floor
(~1% CV) yet is fully consistent with a *systematic* hydration confound.

Source: https://www.bodyspec.com/blog/post/will_drinking_water_affect_my_scan

## 2. Recomposition is real, but glycogen-water inflates the swings

BodySpec client, three scans:

| Date | Body fat % | Total | Fat (lbs) | Lean (lbs) |
|---|---|---|---|---|
| 2016-06-02 | 31.1 | 199.6 | 62.1 | 131.1 |
| 2016-09-19 | 29.3 | 185.6 | 54.3 | 124.6 |
| 2016-10-31 | 23.2 | 177.8 | 41.2 | 130.2 |

- Low-cal/low-carb phase: "lost 6.5 lb muscle" — largely glycogen-water depletion.
- After adding carbs back: "gained back 5.6 lb muscle" in 6 weeks — largely
  glycogen-water repletion, not pure tissue.

Takeaways: (a) fat-loss + lean-gain simultaneously **is** legitimate, so the
direction of my result is plausible; (b) even BodySpec's showcase recomp shows
multi-pound lean swings driven by carb/water status, reinforcing that magnitude —
not direction — is what measurement uncertainty puts in question; (c) a realistic
"real muscle" rate is ~0.5–1 lb/week (their 5.6 lb / 6 weeks ≈ 0.93 lb/wk).

Source: https://www.bodyspec.com/blog/post/lose_fat_and_gain_muscle_is_it_possible

## 3. Training onset → newbie gains + glycogen loading

Sam began consistent weight training right after scan 1 (Strong logging starts
2026-04-16; training began ~2026-04-02). This adds a genuine third driver of the
lean reading:

- **Newbie gains.** An untrained beginner accrues real muscle fastest in the first
  weeks — credibly ~0.5–1.0 lb/week early on (`NEWBIE_MUSCLE_LB_PER_WEEK_MAX`),
  so up to ~4 lb of *real* muscle over the 30-day window is plausible.
- **Training-onset glycogen loading.** Newly trained muscle stores more glycogen,
  and each gram of glycogen binds ~3 g of water — all of which DEXA reads as lean.
  So starting to train inflates "lean mass" via water on top of any real tissue.

This means the lean gain is best read as a *mixture*, not one cause.

## How Phase 4 uses this

`measurement_uncertainty.py` decomposes the observed lean delta into **three**
buckets rather than asserting it as muscle:
1. **Random precision** — propagated from per-scan CV (~1% lean). Gives the ±band.
2. **Systematic hydration / glycogen water** — using `LEAN_LB_PER_GALLON`, express
   the lean gain as "equivalent gallons of water" and show how small a hydration /
   glycogen difference is needed to explain a large share of it.
3. **Plausible real (newbie) muscle** — bounded at ~1 lb/week over the window
   (≈ 4 lb) given the untrained-beginner starting point.

The honest conclusion: the +8.4 lb lean is a real-muscle component (elevated by
newbie status) **plus** a glycogen/hydration-water component, with random precision
a minor term — not 8.4 lb of muscle.
