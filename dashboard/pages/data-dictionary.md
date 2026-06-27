---
title: Data Dictionary
---

<div class="sm-eyebrow">§ 7.0 — DATA DICTIONARY · EVERY VARIABLE, SOURCE, AND CAVEAT</div>

_If a number appears on this site, it is defined here: what it means, its unit, where it comes from, and how far to trust it._

## § 7.1 — Sources & provenance

| Source | What it provides | Reliability note |
|---|---|---|
| **BodySpec DEXA** (×2) | Body composition — total + regional fat/lean/bone mass, body-fat % | Gold-standard outcome, ±~0.5–1% per scan; lean includes water |
| **Apple Health** | Active/basal energy, heart rate, resting HR, HRV, sleep, VO₂max | Dense; device-dependent; protein sync is inflated |
| **LoseIt food logs** | Daily calories + protein | Canonical for protein & intake; only Date/Calories/Protein trusted |
| **Strong** | Per-set weight × reps by exercise | Logging starts 2026-04-16 (mid-window) |
| **NHANES** (public) | National DXA + demographics reference | Benchmark only; disabled offline |
| **ACSM / BodySpec blog** | Protein ranges; hydration coefficient | Published guidance / vendor experiment |

The analysis **window** is 2026-04-02 → 2026-05-02 (the two scans). Sources are most reliable inside it.

## § 7.2 — Body composition (DEXA)

| Variable | Definition | Unit |
|---|---|---|
| `fat_pct` | Body fat as a share of total mass | % |
| `lean_mass_lbs` | Non-bone, non-fat tissue — **includes water, blood, glycogen fluid** | lb |
| `fat_mass_lbs` | Fat tissue | lb |
| `lean_t0` / `lean_t1` | Lean mass at scan 1 / scan 2 | lb |
| `lean_delta` | `lean_t1 − lean_t0` (per region or total) | lb |
| `lean_pct_change` | `100 × lean_delta / lean_t0` — **proportional** change, the correct hypertrophy metric (absolute lbs favors large groups) | % |
| `lean_pct_band95` | the 95% precision band as a share of baseline (`band95 / lean_t0`) — wider for small regions | ± % |
| `fat_delta` | `fat_t1 − fat_t0` | lb |
| `fat_pct_change` | `100 × fat_delta / fat_t0` | % |
| `lean_delta_band95` | 95% measurement band on the lean delta, from 1% per-scan CV in quadrature | ± lb |
| `lean_is_resolvable` | `abs(lean_delta) > lean_delta_band95` — does the change beat random noise? | bool |

> `lean_is_resolvable = true` rules out *random* precision error only. It does **not** mean the change is muscle — systematic hydration error is a separate, larger effect (see the decomposition).

## § 7.3 — The lean-gain decomposition

| Variable | Definition |
|---|---|
| `real_muscle_lbs` | `min(lean_delta, 4.29)` — plausible newbie muscle, capped at 1 lb/wk × 30/7 |
| `water_lbs` | `lean_delta − real_muscle_lbs` — remainder attributed to glycogen/hydration |
| `water_gallons` | `water_lbs / 7.4` — water-equivalent, via BodySpec's gallon experiment |
| `water_pct` | `water_lbs / lean_delta` — share of the "gain" that is likely not muscle |

## § 7.4 — Energy & nutrition

| Variable | Definition | Unit |
|---|---|---|
| `active_kcal` | Active energy burned (movement) | kcal |
| `basal_kcal` | Basal/resting energy | kcal |
| `tdee_kcal` | `active_kcal + basal_kcal` | kcal |
| `intake_kcal` | Food calories from LoseIt | kcal |
| `net_balance_kcal` | `intake_kcal − tdee_kcal` (negative = deficit) | kcal |
| `cumulative_net_kcal` | Sum of net balance over logged window days | kcal |
| `implied_fat_change_lbs` | `cumulative_net_kcal / 3500` | lb |
| `observed_fat_delta_lbs` | DEXA-measured total fat change | lb |
| `fat_reconciliation_gap_lbs` | `observed − implied` | lb |
| `protein_g` | Daily protein (LoseIt food logs) | g |
| `protein_g_per_kg` | `protein_g / (weight_lbs / 2.20462)` | g/kg |
| `ah_protein_g` | Apple Health protein — **cross-check only, ~2× inflated** | g |

## § 7.5 — Training & recovery

| Variable | Definition | Unit |
|---|---|---|
| `volume_lbs` | `Σ (weight × reps)` over working sets, by region/day | lb |
| `working_sets` | Count of non-warm-up sets | n |
| `region` | DEXA region an exercise maps to (arms/legs/trunk) — **shoulders → arms** | — |
| `resting_hr_bpm` | Daily mean resting heart rate | bpm |
| `hrv_sdnn_ms` | Heart-rate variability, SDNN | ms |
| `sleep_hours` | Time asleep (summed asleep segments) | h |

## § 7.6 — Population benchmarks

| Variable | Definition |
|---|---|
| `pct20_bf … pct80_bf` | Body-fat % cut points by sex + age band; e.g. for men 20–29: 16 / 20 / 24 / 27. A value below `pct20_bf` is leaner than ~80% of the group |
| `dim_acsm_targets` | Reference ranges — protein 1.6–2.2 g/kg (hypertrophy), volume guidance |

## § 7.7 — Threats to validity (read before drawing conclusions)

- **DEXA lean = tissue + water.** The single largest confound; the whole centerpiece exists to address it.
- **Window/logging mismatch.** Strong logging covers ~11 of 31 window days, so regional volume understates true training.
- **Small n.** Two DEXA endpoints and three regions — correlations are illustrative, not significant.
- **Model approximations.** 3,500 kcal/lb and a flat 1% CV are first-order assumptions, exposed as tunable parameters, not ground truth.
- **Single subject.** Everything here describes one person over one month; nothing generalizes.

<div class="sm-meta">↳ how these are computed: [methods](/methods) · why it's framed this way: [about](/about)</div>

<style>
  .sm-eyebrow { font-family: 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #847f74; font-size: 11px; }
  .sm-meta { font-family: 'IBM Plex Mono', monospace; color: #847f74; font-size: 11px; margin-top: .5rem; }
</style>
