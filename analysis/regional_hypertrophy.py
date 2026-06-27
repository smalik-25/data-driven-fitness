"""Q2: Do the regions trained most show the most hypertrophy?

The right hypertrophy metric is **proportional** lean change (% of baseline), not
absolute lbs — a small group (arms) can't add as many absolute lbs as the trunk,
but may grow more as a share of itself. This script ranks regions by % change and
contrasts that with the absolute ranking.

Finding: by absolute lbs, volume does NOT predict lean gain (trunk gains most,
arms most-trained but least lbs). By % change, the ranking flips — arms grow the
most proportionally — and matches the training-volume ranking. Caveats hold: ~11
logged days, n=3, and the lean deltas still carry the hydration/glycogen confound
(glycogen loads preferentially into the trained muscles, pointing the same way).
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
    dexa = {
        r: con.execute(
            "select lean_t0, lean_delta, lean_pct_change, lean_pct_band95 "
            "from mart_dexa_change where region = ?",
            [r],
        ).fetchone()
        for r in REGIONS
    }
    vol = {r: 0.0 for r in REGIONS}
    for region, v in con.execute(
        "select region, sum(volume_lbs) as v from silver_daily_training_volume "
        "where workout_date between ? and ? group by region",
        [WINDOW_START, WINDOW_END],
    ).fetchall():
        if region in vol:
            vol[region] = v or 0.0

    abs_delta = {r: dexa[r][1] for r in REGIONS}
    pct_change = {r: dexa[r][2] for r in REGIONS}
    vol_vals = [vol[r] for r in REGIONS]

    rho_pct, _ = stats.spearmanr([pct_change[r] for r in REGIONS], vol_vals)
    rho_abs, _ = stats.spearmanr([abs_delta[r] for r in REGIONS], vol_vals)

    result = {
        "regions": list(REGIONS),
        "lean_pct_change": {r: pct_change[r] for r in REGIONS},
        "lean_pct_band95": {r: dexa[r][3] for r in REGIONS},
        "lean_delta_lbs": {r: round(abs_delta[r], 2) for r in REGIONS},
        "window_volume_lbs": {r: round(vol[r], 0) for r in REGIONS},
        "spearman_pct_vs_volume_n3": round(float(rho_pct), 3),
        "spearman_abs_vs_volume_n3": round(float(rho_abs), 3),
        "reading": (
            "Proportional growth tracks training volume (rho="
            f"{round(float(rho_pct), 2)}); absolute lbs does not "
            f"(rho={round(float(rho_abs), 2)}). The metric choice reverses the result."
        ),
        "caveat": "n=3, ~11 logged days; lean deltas carry the hydration/glycogen confound",
    }
    _plot(pct_change, abs_delta, vol)
    return result


def _plot(pct: dict, absd: dict, vol: dict) -> None:
    out = ensure_output_dir() / "regional_hypertrophy.png"
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(11, 4.5))

    x = range(len(REGIONS))
    # Left: proportional growth (the right metric) vs volume
    axl.bar([i - 0.2 for i in x], [pct[r] for r in REGIONS], width=0.4,
            color="#2E7D5B", label="Lean Δ %")
    axl.set_ylabel("Lean Δ (% of baseline)", color="#2E7D5B")
    axl.set_xticks(list(x))
    axl.set_xticklabels([r.title() for r in REGIONS])
    ax2 = axl.twinx()
    ax2.plot([i for i in x], [vol[r] for r in REGIONS], "o-", color="#5B9BD5",
             label="Volume")
    ax2.set_ylabel("Volume (lbs)", color="#5B9BD5")
    axl.set_title("Proportional growth tracks volume (the right metric)")

    # Right: absolute lbs vs volume — the misleading view
    axr.bar([i - 0.2 for i in x], [absd[r] for r in REGIONS], width=0.4,
            color="#847f74", label="Lean Δ lbs")
    axr.set_ylabel("Lean Δ (lbs)", color="#847f74")
    axr.set_xticks(list(x))
    axr.set_xticklabels([r.title() for r in REGIONS])
    ax3 = axr.twinx()
    ax3.plot([i for i in x], [vol[r] for r in REGIONS], "o-", color="#5B9BD5")
    ax3.set_ylabel("Volume (lbs)", color="#5B9BD5")
    axr.set_title("Absolute lbs does not (favors large groups)")

    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    result = compute()
    print("=== Q2 Regional hypertrophy: proportional vs absolute ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return result


if __name__ == "__main__":
    main()
