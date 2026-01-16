"""
Download and parse Ken French portfolio returns (monthly).

Outputs:
- data/processed/returns_monthly.parquet
"""

from pathlib import Path
import io
import zipfile
import requests
import pandas as pd

URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/25_Portfolios_5x5_CSV.zip"

def main():
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    processed = root / "data" / "processed"
    raw.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    zip_path = raw / "25_Portfolios_5x5_CSV.zip"
    if not zip_path.exists():
        r = requests.get(URL, timeout=60)
        r.raise_for_status()
        zip_path.write_bytes(r.content)

    with zipfile.ZipFile(zip_path, "r") as z:
        name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        text = z.read(name).decode("utf-8", errors="replace")

    lines = text.splitlines()

    # header looks like: ",SMALL LoBM, ..., BIG HiBM"
    header_i = next(i for i,l in enumerate(lines) if l.strip().startswith(","))
    data = []
    for line in lines[header_i + 1:]:
        if not line.strip():
            break
        data.append(line)

    df = pd.read_csv(io.StringIO("\n".join([lines[header_i]] + data)))
    df.rename(columns={df.columns[0]: "date"}, inplace=True)

    df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m")
    df = df.apply(pd.to_numeric, errors="ignore")

    # Simple example: equal-weight average portfolio return
    df["ret"] = df.drop(columns=["date"]).mean(axis=1) / 100.0

    returns = df[["date", "ret"]]
    returns.to_parquet(processed / "returns_monthly.parquet", index=False)
    print("Wrote data/processed/returns_monthly.parquet")

if __name__ == "__main__":
    main()