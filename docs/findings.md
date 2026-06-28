# Findings (Phase 4)

Results over the analysis window (2026-04-02 → 2026-05-02, the two DEXA scans).
All body-composition changes are reported with their measurement caveats. See
`docs/measurement_notes.md`.

## The headline: the +8.4 lb "lean gain" is not 8.4 lb of muscle

The two scans report **+8.4 lb lean** and **−9.8 lb fat** in 30 days. Decomposed:

| Component | Amount | Basis |
|---|---|---|
| Plausible real (newbie) muscle | ≤ **4.3 lb** | ~1 lb/wk cap for an untrained beginner |
| Glycogen / hydration water | ~ **4.1 lb** (≈49%, ≈0.56 gal) | BodySpec's 7.4 lb-lean-per-gallon experiment |
| Random precision band (95%) | ± **3.4 lb** | 1% per-scan CV, propagated |

The whole +8.4 lb is equivalent to about 1.1 gallons of water. It clears the
*random* noise floor, but it's also fully consistent with a real but modest
muscle gain (elevated by newbie status) inflated by training-onset glycogen
loading and a scan-day hydration difference. **What's in question is the size of
the change, not its direction.**

## The five questions

1. **Energy balance predicts the fat change, not the lean one.** Cumulative
   −39,190 kcal over 30 logged days implies −11.2 lb fat; DEXA observed −9.8 lb
   (gap **1.4 lb**, a good reconciliation). Energy balance doesn't explain the
   lean change.
2. **Regional hypertrophy tracks volume — once measured proportionally.** The
   right metric is % change, not absolute lbs (absolute favors large groups). By
   % change, arms grew most (+14.1%) on the most volume, then trunk (+7.8%), then
   legs (+5.4%), ranking volume **exactly** (Spearman +1.0). By absolute lbs the
   trunk "wins" and the correlation is −0.5. The metric choice reverses the
   conclusion. Caveat: glycogen loads into trained muscles, so part of the
   proportional gain is trained-muscle water; n=3, ~11 logged days.
3. **Protein was in the hypertrophy range.** Mean **1.83 g/kg** (ACSM 1.6–2.2),
   inside the range on 16 of 30 logged days.
4. **No overreaching signature.** Weak correlations between training load and
   resting HR (+0.13), HRV (−0.19), sleep (+0.04); mean sleep ~6.9 h.
5. **Volume "efficiency" is directional only.** Trunk shows the highest apparent
   lean-per-volume and arms the lowest, but the numerator is confounded and the
   denominator covers only ~11 logged days. It isn't a causal efficiency.

## Caveats that apply throughout

- **Strong logging starts 2026-04-16**, so only ~11 of 31 window days have lifts.
- **DEXA lean readings include water**, and the centerpiece is built around that.
- Small n (two DEXA endpoints, three regions), so correlations are illustrative.
