import pandas as pd
import numpy as np
import re

def extract_alan_gray_balanced(file_path):
    df_raw = pd.read_excel(file_path, header=None)

    # ---- Find header row dynamically ----
    header_row = None
    for i, row in df_raw.iterrows():
        row_lower = row.astype(str).str.lower()
        if row_lower.str.contains("date").any() and row_lower.str.contains("total fund").any():
            header_row = i
            break
    if header_row is None:
        raise ValueError("Header row not found (DATE / Total Fund Size).")

    # ---- Read with proper header ----
    df = pd.read_excel(file_path, header=header_row)

    # Clean column names (handles line breaks)
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Required columns
    required = ["DATE", "Net", "Total Fund Size (A$m)"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing expected column: {c}. Found: {list(df.columns)}")

    # ---- Keep ONLY true date rows (drops 'Latest 3 months', 'FYTD', etc.) ----
    df["DATE_dt"] = pd.to_datetime(df["DATE"], errors="coerce")
    df = df[df["DATE_dt"].notna()].copy()

    # ---- Clean numeric columns ----
    # Total fund size: should be numeric already, but force it
    df["TotalFundSize_num"] = pd.to_numeric(df["Total Fund Size (A$m)"], errors="coerce")

    # Net: could be numeric or like "0.35%"
    df["Net_str"] = df["Net"].astype(str).str.replace("%", "", regex=False).str.strip()
    df["Net_num"] = pd.to_numeric(df["Net_str"], errors="coerce")

    # Drop rows where we can't get fund size or net
    df = df[df["TotalFundSize_num"].notna() & df["Net_num"].notna()].copy()

    if df.empty:
        raise ValueError("No valid dated rows found with numeric Total Fund Size and Net.")

    # ---- Pick the last dated row ----
    df = df.sort_values("DATE_dt")
    last_row = df.iloc[-1]

    # NAV is in A$m → multiply to actual number
    nav_value = float(last_row["TotalFundSize_num"]) * 1_000_000
    mtd_value = float(last_row["Net_num"])

    return nav_value, mtd_value
