"""Q3: Was protein intake in the range associated with lean retention/gain?

With only two DEXA endpoints we can't do a true daily protein-vs-lean correlation,
so this benchmarks in-window daily protein (g/kg, from the LoseIt food logs) against
the ACSM/ISSN hypertrophy range, and shows the daily series + the Apple Health
cross-check (which is ~2x inflated).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis._common import connect, ensure_output_dir


def compute() -> dict:
    con = connect()
    daily = con.execute(
        "select day, protein_g, protein_g_per_kg from fct_daily "
        "where is_analysis_window and protein_g is not null order by day"
    ).pl()
    acsm = con.execute(
        "select low, high from dim_acsm_targets "
        "where metric = 'protein_intake' and context = 'muscle_hypertrophy'"
    ).fetchone()
    lo, hi = acsm
    mean_gkg = float(daily["protein_g_per_kg"].mean())
    days_in_range = int(
        daily.filter(
            (daily["protein_g_per_kg"] >= lo) & (daily["protein_g_per_kg"] <= hi)
        ).height
    )
    result = {
        "mean_protein_g_per_kg": round(mean_gkg, 2),
        "acsm_hypertrophy_range_g_per_kg": [lo, hi],
        "in_range": lo <= mean_gkg <= hi,
        "days_logged": daily.height,
        "days_within_range": days_in_range,
    }
    _plot(daily, lo, hi)
    return result


def _plot(daily, lo, hi) -> None:
    out = ensure_output_dir() / "protein_lean.png"
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(daily["day"], daily["protein_g_per_kg"], marker="o", color="#2E7D5B",
            label="Protein (g/kg/day)")
    ax.axhspan(lo, hi, color="#5B9BD5", alpha=0.2, label=f"ACSM hypertrophy {lo}-{hi}")
    ax.set_ylabel("Protein (g/kg/day)")
    ax.set_title("In-window protein vs ACSM hypertrophy range")
    ax.legend(fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    result = compute()
    print("=== Q3 Protein vs ACSM range ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return result


if __name__ == "__main__":
    main()
