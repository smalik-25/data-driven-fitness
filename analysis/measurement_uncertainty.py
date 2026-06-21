"""CENTERPIECE: how much of the +lean DEXA change is real muscle?

The two scans report a +8.4 lb lean change in 30 days. This script refuses to
call that "muscle." Instead it decomposes the lean delta into three components:

1. Random precision  — propagated from per-scan CV (~1% lean) -> a +/- noise band.
2. Plausible real (newbie) muscle — Sam started training at scan 1, so bound the
   genuine gain at ~1 lb/week over the window (~4 lb).
3. Glycogen / hydration water — the remainder, expressed in "gallons of water
   equivalent" using BodySpec's own gallon experiment (7.4 lb lean per gallon).

The point: the lean gain clears the *random* noise floor yet is fully consistent
with a real-but-smaller muscle gain inflated by training-onset glycogen and
day-to-day hydration. See docs/measurement_notes.md for sources.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis._common import (
    NEWBIE_MUSCLE_LB_PER_WEEK_MAX,
    WINDOW_DAYS,
    connect,
    ensure_output_dir,
    gallons_equivalent,
)


def compute() -> dict:
    con = connect()
    total = con.execute(
        "select lean_t0, lean_t1, lean_delta, lean_delta_band95 "
        "from mart_dexa_change where region = 'total'"
    ).fetchone()
    lean_t0, lean_t1, lean_delta, band95 = total

    # Bucket 2: plausible real muscle for an untrained beginner over the window.
    max_real_muscle = NEWBIE_MUSCLE_LB_PER_WEEK_MAX * (WINDOW_DAYS / 7.0)
    real_muscle = min(lean_delta, max_real_muscle)

    # Bucket 3: the remainder, attributable to glycogen/hydration water.
    water_component = max(lean_delta - real_muscle, 0.0)

    result = {
        "lean_delta_lbs": round(lean_delta, 2),
        "precision_band95_lbs": round(band95, 2),
        "clears_noise_floor": abs(lean_delta) > band95,
        "max_plausible_newbie_muscle_lbs": round(max_real_muscle, 2),
        "attributed_real_muscle_lbs": round(real_muscle, 2),
        "attributed_water_lbs": round(water_component, 2),
        "water_as_gallons": round(gallons_equivalent(water_component), 2),
        "whole_delta_as_gallons": round(gallons_equivalent(lean_delta), 2),
        "share_explained_by_water_pct": round(100 * water_component / lean_delta, 1),
    }
    _plot(lean_delta, band95, real_muscle, water_component, result)
    return result


def _plot(lean_delta, band95, real_muscle, water, result) -> None:
    out = ensure_output_dir() / "measurement_uncertainty.png"
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.bar(0, real_muscle, color="#2E7D5B", label="Plausible real (newbie) muscle")
    ax.bar(0, water, bottom=real_muscle, color="#5B9BD5",
           label="Glycogen / hydration water")
    # random precision band as an error bar on the total
    ax.errorbar(0, real_muscle + water, yerr=band95, fmt="none",
                ecolor="#444", capsize=8, lw=2, label="95% precision band")

    ax.set_xlim(-1, 2.2)
    ax.set_xticks([])
    ax.set_ylabel("Lean mass change (lbs)")
    ax.set_title(
        f"Observed +{lean_delta:.1f} lb 'lean gain' decomposed\n"
        f"≈ {result['water_as_gallons']:.1f} gallons of water explains the non-muscle part"
    )
    ax.annotate(
        f"real muscle ≤ {real_muscle:.1f} lb\nwater ≈ {water:.1f} lb "
        f"({result['share_explained_by_water_pct']:.0f}%)",
        xy=(0.35, (real_muscle + water) / 2), fontsize=10,
    )
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    result = compute()
    print("=== Measurement uncertainty: the lean 'gain' ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print(
        "\nReading: the +{d} lb lean change clears the random noise band (±{b} lb), "
        "but at most ~{m} lb is plausible newbie muscle in 30 days; the remaining "
        "~{w} lb (~{g} gal of water) is consistent with training-onset glycogen "
        "loading and scan-day hydration. Not 8 lb of muscle.".format(
            d=result["lean_delta_lbs"], b=result["precision_band95_lbs"],
            m=result["attributed_real_muscle_lbs"], w=result["attributed_water_lbs"],
            g=result["water_as_gallons"],
        )
    )
    return result


if __name__ == "__main__":
    main()
