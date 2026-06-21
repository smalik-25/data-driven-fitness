"""Q2: Do the regions that gained the most lean track training volume by region?

Joins per-region DEXA lean delta (arms/legs/trunk) to in-window training volume.
Reports the rank agreement and a correlation. Heavily caveated: only ~11 of 31
window days have logged lifts (Strong starts 2026-04-16), and the lean deltas
carry the hydration/glycogen confound from the centerpiece.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

from analysis._common import WINDOW_END, WINDOW_START, connect, ensure_output_dir

REGIONS = ("arms", "legs", "trunk")


def compute() -> dict:
    con = connect()
    lean = {
        r: con.execute(
            "select lean_delta from mart_dexa_change where region = ?", [r]
        ).fetchone()[0]
        for r in REGIONS
    }
    vol = {r: 0.0 for r in REGIONS}
    rows = con.execute(
        "select region, sum(volume_lbs) as v from silver_daily_training_volume "
        "where workout_date between ? and ? group by region",
        [WINDOW_START, WINDOW_END],
    ).fetchall()
    for region, v in rows:
        if region in vol:
            vol[region] = v or 0.0

    lean_vals = [lean[r] for r in REGIONS]
    vol_vals = [vol[r] for r in REGIONS]
    # Spearman rank (3 points — illustrative only, flagged as such)
    rho, _ = stats.spearmanr(lean_vals, vol_vals)

    result = {
        "regions": list(REGIONS),
        "lean_delta_lbs": {r: round(lean[r], 2) for r in REGIONS},
        "window_volume_lbs": {r: round(vol[r], 0) for r in REGIONS},
        "spearman_rho_n3_illustrative": round(float(rho), 3),
        "caveat": "n=3 regions, ~11 logged days, lean deltas carry hydration confound",
    }
    _plot(lean, vol)
    return result


def _plot(lean: dict, vol: dict) -> None:
    out = ensure_output_dir() / "regional_hypertrophy.png"
    fig, ax1 = plt.subplots(figsize=(7.5, 4.5))
    x = range(len(REGIONS))
    ax1.bar([i - 0.2 for i in x], [lean[r] for r in REGIONS], width=0.4,
            color="#2E7D5B", label="Lean Δ (lbs)")
    ax1.set_ylabel("Lean Δ (lbs)", color="#2E7D5B")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([r.title() for r in REGIONS])
    ax2 = ax1.twinx()
    ax2.bar([i + 0.2 for i in x], [vol[r] for r in REGIONS], width=0.4,
            color="#5B9BD5", label="Volume (lbs)")
    ax2.set_ylabel("In-window training volume (lbs)", color="#5B9BD5")
    ax1.set_title("Regional lean change vs training volume (window; n small)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    result = compute()
    print("=== Q2 Regional hypertrophy vs volume ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return result


if __name__ == "__main__":
    main()
