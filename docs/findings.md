# Findings (Phase 4)

Results over the analysis window (2026-04-02 → 2026-05-02, the two DEXA scans).
All body-composition changes are reported with their measurement caveats — see
`docs/measurement_notes.md`.

## The headline: the +8.4 lb "lean gain" is not 8.4 lb of muscle

The two scans report **+8.4 lb lean** and **−9.8 lb fat** in 30 days. Decomposed:

| Component | Amount | Basis |
|---|---|---|
| Plausible real (newbie) muscle | ≤ **4.3 lb** | ~1 lb/wk cap for an untrained beginner |
| Glycogen / hydration water | ~ **4.1 lb** (≈49%, ≈0.56 gal) | BodySpec's 7.4 lb-lean-per-gallon experiment |
| Random precision band (95%) | ± **3.4 lb** | 1% per-scan CV, propagated |

The whole +8.4 lb is equivalent to ~1.1 gallons of water. It clears the *random*
noise floor, but is fully consistent with a real-but-modest muscle gain (elevated
by newbie status) inflated by training-onset glycogen loading and scan-day
hydration. **Magnitude, not direction, is what's in question.**

## The five questions

1. **Energy balance predicts fat, not lean.** Cumulative −39,190 kcal over 30
   logged days implies −11.2 lb fat; DEXA observed −9.8 lb (gap **1.4 lb** — a
   good reconciliation). The lean change is *not* explained by energy balance.
2. **Regional volume did NOT track regional lean gain** (Spearman −0.5, n=3).
   Arms got the most volume (46.5k lb) but the least lean change (+1.9 lb); trunk
   gained the most lean (+4.2 lb) at mid volume. Consistent with the water
   confound swamping the training signal over a short, partially-logged window.
3. **Protein was in the hypertrophy range.** Mean **1.83 g/kg** (ACSM 1.6–2.2),
   inside the range on 16 of 30 logged days.
4. **No overreaching signature.** Weak correlations between training load and
   resting HR (+0.13), HRV (−0.19), sleep (+0.04); mean sleep ~6.9 h.
5. **Volume "efficiency" is directional only.** Trunk shows the highest apparent
   lean-per-volume, arms the lowest — but the numerator is confounded and the
   denominator covers ~11 logged days. Not a causal efficiency.

## Caveats that apply throughout

- **Strong logging starts 2026-04-16**, so only ~11 of 31 window days have lifts.
- **DEXA lean readings include water**; the centerpiece is built around that.
- Small n (two DEXA endpoints, 3 regions) — correlations are illustrative.
