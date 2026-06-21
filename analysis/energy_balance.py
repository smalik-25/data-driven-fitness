"""Q1: Did measured calorie balance predict the DEXA fat/lean change?

Reads the reconciliation mart: cumulative net energy balance over the window vs
the DEXA-observed change. The fat side should roughly reconcile (≈3500 kcal/lb);
the lean side is left unexplained by energy balance (see measurement_uncertainty).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis._common import connect, ensure_output_dir


def compute() -> dict:
    con = connect()
    row = con.execute("select * from mart_recomp_reconciliation").pl().to_dicts()[0]
    _plot(row)
    return row


def _plot(row: dict) -> None:
    out = ensure_output_dir() / "energy_balance.png"
    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels = ["Implied by\nenergy balance", "Observed\n(DEXA)"]
    values = [row["implied_fat_change_lbs"], row["observed_fat_delta_lbs"]]
    ax.bar(labels, values, color=["#5B9BD5", "#2E7D5B"])
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:.1f} lb", ha="center", va="top", fontsize=11)
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_ylabel("Fat mass change (lbs)")
    ax.set_title(
        f"Fat change reconciles within {abs(row['fat_reconciliation_gap_lbs']):.1f} lb; "
        f"lean +{row['lean_change_unexplained_by_energy_lbs']:.1f} lb is unexplained"
    )
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    row = compute()
    print("=== Q1 Energy balance reconciliation ===")
    for k, v in row.items():
        print(f"  {k}: {v}")
    print(
        f"\nReading: over {row['days_with_intake']} logged days the cumulative "
        f"{row['cumulative_net_kcal']:.0f} kcal balance implies "
        f"{row['implied_fat_change_lbs']:.1f} lb of fat change; DEXA observed "
        f"{row['observed_fat_delta_lbs']:.1f} lb (gap {row['fat_reconciliation_gap_lbs']:.1f} lb). "
        f"The +{row['lean_change_unexplained_by_energy_lbs']:.1f} lb lean is NOT explained by "
        "energy balance — see measurement_uncertainty."
    )
    return row


if __name__ == "__main__":
    main()
