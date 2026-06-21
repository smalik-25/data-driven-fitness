"""Q5: Lean mass gained per unit of training volume, per muscle region.

Divides each region's DEXA lean delta by its in-window training volume. This is the
*least* trustworthy metric in the project and is reported with that warning loud:
the numerator (lean delta) is confounded by hydration/glycogen and newbie gains,
and the denominator covers only ~11 logged days. Treat as directional, not causal.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis._common import WINDOW_END, WINDOW_START, connect, ensure_output_dir

REGIONS = ("arms", "legs", "trunk")


def compute() -> dict:
    con = connect()
    eff = {}
    for r in REGIONS:
        lean = con.execute(
            "select lean_delta from mart_dexa_change where region = ?", [r]
        ).fetchone()[0]
        vrow = con.execute(
            "select sum(volume_lbs) from silver_daily_training_volume "
            "where region = ? and workout_date between ? and ?",
            [r, WINDOW_START, WINDOW_END],
        ).fetchone()
        vol = vrow[0] or 0.0
        eff[r] = {
            "lean_delta_lbs": round(lean, 2),
            "window_volume_lbs": round(vol, 0),
            "lean_lb_per_1000lb_volume": round(1000 * lean / vol, 3) if vol else None,
        }
    result = {
        "per_region": eff,
        "warning": (
            "Numerator confounded by hydration/glycogen + newbie gains; denominator "
            "covers ~11 logged days. Directional only — not a causal efficiency."
        ),
    }
    _plot(eff)
    return result


def _plot(eff: dict) -> None:
    out = ensure_output_dir() / "volume_efficiency.png"
    fig, ax = plt.subplots(figsize=(7, 4.5))
    vals = [eff[r]["lean_lb_per_1000lb_volume"] or 0 for r in REGIONS]
    ax.bar([r.title() for r in REGIONS], vals, color="#2E7D5B")
    ax.set_ylabel("Lean Δ per 1,000 lb volume")
    ax.set_title("Apparent lean gain per unit volume (directional only)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    result = compute()
    print("=== Q5 Volume efficiency (directional only) ===")
    for r in REGIONS:
        print(f"  {r}: {result['per_region'][r]}")
    print(f"  warning: {result['warning']}")
    return result


if __name__ == "__main__":
    main()
