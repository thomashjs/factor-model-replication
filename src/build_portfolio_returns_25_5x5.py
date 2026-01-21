"""
Download and parse Ken French 25 Size-B/M portfolios (5x5), monthly returns.

Output (decimal returns):
- data/processed/portfolios_25_5x5_monthly.parquet
  columns: date, <25 portfolio columns>
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
        csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        text = z.read(csv_name).decode("utf-8", errors="replace")

    lines = text.splitlines()

    # Find first header line for the monthly table: it starts with a comma (blank first col)
    header_i = next(i for i, l in enumerate(lines) if l.strip().startswith(","))

    # Read rows until first blank line (end of monthly table)
    rows = [lines[header_i]]
    for line in lines[header_i + 1:]:
        if not line.strip():
            break
        rows.append(line)

    df = pd.read_csv(io.StringIO("\n".join(rows)))

    # First column is YYYYMM date (unnamed)
    df.rename(columns={df.columns[0]: "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), format="%Y%m")

    # Convert all portfolio columns from percent to decimal
    for c in df.columns:
        if c != "date":
            df[c] = pd.to_numeric(df[c], errors="coerce") / 100.0

    out = processed / "portfolios_25_5x5_monthly.parquet"
    df.to_parquet(out, index=False)
    print(f"Wrote {out} with {df.shape[1]-1} portfolios and {len(df)} months.")

if __name__ == "__main__":
    main()
