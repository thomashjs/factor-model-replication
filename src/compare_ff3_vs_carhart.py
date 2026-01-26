"""
Merge FF3 results with Carhart results and make comparison columns.

Inputs (decimal units):
- reports/carhart_25_5x5_results.csv (portfolio, alphas, betas, t-values, and r2 statistics)
- reports/ff3_25_5x5_results.csv     (portfolio, alphas, betas, t-values, and r2 statistics)

Output:
- reports/ff3_vs_carhart_comparison.csv
"""
import pandas as pd
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    carhart_path = root / "reports/carhart_25_5x5_results.csv"
    ff3_path = root / "reports/ff3_25_5x5_results.csv"

    carhart_df = pd.read_csv(carhart_path)
    ff3_df = pd.read_csv(ff3_path)

    merged_df = carhart_df.merge(ff3_df, on="portfolio", how="inner", suffixes=("_carhart", "_ff3"))
    merged_df["delta_alpha"] = merged_df["alpha_carhart"] - merged_df["alpha_ff3"]
    merged_df["delta_r2"] = merged_df["r2_carhart"] - merged_df["r2_ff3"]
    cleaned_df = merged_df[[
        "portfolio",
        "alpha_ff3",
        "alpha_carhart",
        "delta_alpha",
        "r2_ff3",
        "r2_carhart",
        "delta_r2",
    ]].sort_values("portfolio")

    out_path = root / "reports/ff3_vs_carhart_comparison.csv"
    cleaned_df.round(6).to_csv(out_path, index=False)

    print(f"Wrote {out_path}")
    print(cleaned_df.head())

if __name__ == "__main__":
    main()