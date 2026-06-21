"""Q4: Did sleep, HRV, or resting HR move with training load?

Looks for overreaching signatures in the window: rising resting HR, falling HRV,
or falling sleep as training volume ramps. Correlations are illustrative given the
short window and that logged lifts start mid-window.
"""

from __future__ import annotations

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis._common import connect, ensure_output_dir


def compute() -> dict:
    con = connect()
    df = con.execute(
        "select day, total_volume_lbs, resting_hr_bpm, hrv_sdnn_ms, sleep_hours "
        "from fct_daily where is_analysis_window order by day"
    ).pl()

    def corr(a: str, b: str) -> float | None:
        sub = df.select([a, b]).drop_nulls()
        if sub.height < 3:
            return None
        x, y = sub[a].to_numpy(), sub[b].to_numpy()
        if x.std() == 0 or y.std() == 0:
            return None
        return round(float(np.corrcoef(x, y)[0, 1]), 3)

    result = {
        "days": df.height,
        "corr_volume_resting_hr": corr("total_volume_lbs", "resting_hr_bpm"),
        "corr_volume_hrv": corr("total_volume_lbs", "hrv_sdnn_ms"),
        "corr_volume_sleep": corr("total_volume_lbs", "sleep_hours"),
        "mean_resting_hr": round(float(df["resting_hr_bpm"].drop_nulls().mean() or 0), 1),
        "mean_hrv_sdnn": round(float(df["hrv_sdnn_ms"].drop_nulls().mean() or 0), 1),
        "mean_sleep_hours": round(float(df["sleep_hours"].drop_nulls().mean() or 0), 2),
        "caveat": "short window, lifts logged from 2026-04-16; correlations illustrative",
    }
    _plot(df)
    return result


def _plot(df) -> None:
    out = ensure_output_dir() / "recovery_load.png"
    fig, ax1 = plt.subplots(figsize=(8.5, 4.5))
    ax1.bar(df["day"], df["total_volume_lbs"], color="#cfe3d6", label="Training volume")
    ax1.set_ylabel("Training volume (lbs)")
    ax2 = ax1.twinx()
    ax2.plot(df["day"], df["resting_hr_bpm"], color="#C0504D", marker=".", label="Resting HR")
    ax2.plot(df["day"], df["hrv_sdnn_ms"], color="#5B9BD5", marker=".", label="HRV (SDNN)")
    ax2.set_ylabel("Resting HR (bpm) / HRV (ms)")
    ax1.set_title("Training load vs recovery signals (window)")
    fig.legend(loc="upper right", fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> dict:
    result = compute()
    print("=== Q4 Recovery vs training load ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return result


if __name__ == "__main__":
    main()
