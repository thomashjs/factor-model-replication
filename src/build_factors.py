"""
Build combined factor dataset from Fama-French 3 factors and momentum factor datasets.
Need to have already downloaded and processed those datasets by using ken_french.py.
"""
import pandas as pd

def main():
    ff3 = pd.read_parquet("data/processed/ff3_monthly.parquet")
    mom = pd.read_parquet("data/processed/mom_monthly.parquet")

    factors = ff3.merge(mom, on="date", how="inner")

    # Convert percent to decimal (Ken French data are in percent)
    for c in factors.columns:
        if c != "date":
            factors[c] = factors[c] / 100.0

    factors.to_parquet("data/processed/factors_monthly.parquet", index=False)
    print("Wrote data/processed/factors_monthly.parquet")
    print("Columns:", factors.columns.tolist())
    print(factors.head())

if __name__ == "__main__":
    main()
