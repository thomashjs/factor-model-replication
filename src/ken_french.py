"""
Download and parse Ken French factor datasets (Fama-French 3 factors, Momentum).
Saves processed datasets as parquet files in data/processed/.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import io
import zipfile
import re
import requests
import pandas as pd

FF3_ZIP_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
MOM_ZIP_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip"

@dataclass(frozen=True)
class Paths:
    root: Path
    raw: Path
    processed: Path

def project_paths() -> Paths:
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    processed = root / "data" / "processed"
    raw.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    return Paths(root=root, raw=raw, processed=processed)

def download(url: str, dest: Path, timeout: int = 60) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest

def _extract_first_csv_bytes(zip_path: Path) -> bytes:
    with zipfile.ZipFile(zip_path, "r") as z:
        csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV found inside {zip_path}")
        # typically only one CSV
        return z.read(csv_names[0])

def _parse_first_table(csv_bytes: bytes) -> pd.DataFrame:
    """
    Parse the FIRST numeric table in a Ken French CSV.
    Works for FF3, Momentum, etc., where the date column is the first column
    and is often unnamed (header starts with a leading comma).
    Stops at the first blank line, so it won't include later tables (annual).
    """
    text = csv_bytes.decode("utf-8", errors="replace")
    lines = text.splitlines()

    # Find the first header line that looks like a CSV header with an empty first field:
    # e.g. ",Mkt-RF,SMB,HML,RF" or ",Mom" or ",WML,RF" etc.
    header_i = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or not s.startswith(","):
            continue
        # must have at least 2 columns, and not be a comment/title line
        parts = [p.strip().strip('"') for p in s.split(",")]
        if len(parts) < 2:
            continue
        if parts[0] != "":
            continue
        # reject obvious non-headers
        if any(("copyright" in p.lower()) or ("ken french" in p.lower()) for p in parts):
            continue
        # accept if there's at least one alphabetic column name after the blank first col
        if any(re.search(r"[A-Za-z]", p) for p in parts[1:]):
            header_i = i
            break

    if header_i is None:
        raise ValueError("Could not locate the first table header (line starting with ',' and column names).")

    # Data starts after header; end at first blank line
    data_start = header_i + 1
    data_end = None
    for j in range(data_start, len(lines)):
        if not lines[j].strip():
            data_end = j
            break
    if data_end is None:
        data_end = len(lines)

    table_block = "\n".join(lines[header_i:data_end])
    df = pd.read_csv(io.StringIO(table_block))

    # First column is the date column (often unnamed)
    first_col = df.columns[0]
    df.rename(columns={first_col: "date"}, inplace=True)

    df["date"] = df["date"].astype(str).str.strip().str.replace('"', "", regex=False)

    # Monthly is YYYYMM; daily is YYYYMMDD
    if df["date"].str.fullmatch(r"\d{6}").all():
        df["date"] = pd.to_datetime(df["date"], format="%Y%m")
    elif df["date"].str.fullmatch(r"\d{8}").all():
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    else:
        raise ValueError("Date column not in YYYYMM or YYYYMMDD format in first table.")

    for c in df.columns:
        if c != "date":
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df

def load_ff3_monthly(force_download: bool = False) -> pd.DataFrame:
    p = project_paths()
    zip_path = p.raw / "F-F_Research_Data_Factors_CSV.zip"
    if force_download or not zip_path.exists():
        download(FF3_ZIP_URL, zip_path)
    df = _parse_first_table(_extract_first_csv_bytes(zip_path))
    return df

def load_mom_monthly(force_download: bool = False) -> pd.DataFrame:
    p = project_paths()
    zip_path = p.raw / "F-F_Momentum_Factor_CSV.zip"
    if force_download or not zip_path.exists():
        download(MOM_ZIP_URL, zip_path)
    df = _parse_first_table(_extract_first_csv_bytes(zip_path))
    return df

if __name__ == "__main__":
    p = project_paths()
    ff3 = load_ff3_monthly()
    mom = load_mom_monthly()

    # Save processed copies (parquet is fast + compact)
    ff3.to_parquet(p.processed / "ff3_monthly.parquet", index=False)
    mom.to_parquet(p.processed / "mom_monthly.parquet", index=False)

    print("FF3 rows:", len(ff3), "cols:", list(ff3.columns))
    print("MOM rows:", len(mom), "cols:", list(mom.columns))
