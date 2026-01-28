"""
Create comparison plots for FF3 vs Carhart results.

Inputs:
- reports/ff3_vs_carhart_comparison.csv

Outputs:
- figures/alpha_ff3_vs_carhart.png
- figures/delta_r2_by_portfolio.png
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    root = Path(__file__).resolve().parents[1]
    comp_path = root / "reports" / "ff3_vs_carhart_comparison.csv"
    fig_dir = root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(comp_path)

    # ---------- Plot 1: alpha scatter ----------
    x = df["alpha_ff3"].astype(float)
    y = df["alpha_carhart"].astype(float)

    plt.figure()
    plt.scatter(x, y)

    # 45-degree line
    lo = min(x.min(), y.min())
    hi = max(x.max(), y.max())
    plt.plot([lo, hi], [lo, hi], linestyle="--")

    plt.xlabel("alpha (FF3)")
    plt.ylabel("alpha (Carhart)")
    plt.title("Alpha: FF3 vs Carhart (45° line)")
    out1 = fig_dir / "alpha_ff3_vs_carhart.png"
    plt.savefig(out1, dpi=200, bbox_inches="tight")
    plt.close()

    # ---------- Plot 2: delta R^2 by portfolio ----------
    d = df[["portfolio", "delta_r2"]].copy()
    d["delta_r2"] = d["delta_r2"].astype(float)
    d = d.sort_values("delta_r2")

    plt.figure(figsize=(8, 10))
    plt.scatter(d["delta_r2"], d["portfolio"])
    plt.axvline(0.0, linestyle="--")
    plt.xlabel("delta R2 (Carhart − FF3)")
    plt.ylabel("portfolio")
    plt.title("ΔR2 by portfolio")
    out2 = fig_dir / "delta_r2_by_portfolio.png"
    plt.savefig(out2, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Wrote {out1}")
    print(f"Wrote {out2}")

if __name__ == "__main__":
    main()