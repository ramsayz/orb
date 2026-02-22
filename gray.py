import pandas as pd
import numpy as np
import re

def extract_alan_gray_balanced(file_path):
    
    # Read raw (no header assumption)
    df_raw = pd.read_excel(file_path, header=None)
    
    # -------- Find header row dynamically --------
    header_row = None
    
    for i, row in df_raw.iterrows():
        row_values = row.astype(str).str.lower().tolist()
        if "date" in row_values and any("total fund size" in str(x).lower() for x in row_values):
            header_row = i
            break
    
    if header_row is None:
        raise ValueError("Header row not found.")
    
    # -------- Read again using correct header --------
    df = pd.read_excel(file_path, header=header_row)
    
    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=True)
    )
    
    # -------- Keep only rows with DATE present --------
    df = df[df["DATE"].notna()]
    
    # Remove rows where Total Fund Size is missing
    df = df[df["Total Fund Size (A$m)"].notna()]
    
    # Sort by DATE (important safety)
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    df = df.sort_values("DATE")
    
    # -------- Take last valid row --------
    last_row = df.iloc[-1]
    
    # ==========================
    # NAV Extraction
    # ==========================
    nav_millions = last_row["Total Fund Size (A$m)"]
    nav_value = float(nav_millions) * 1_000_000   # convert from A$m
    
    # ==========================
    # MTD Extraction
    # ==========================
    mtd_raw = last_row["Net"]
    
    if isinstance(mtd_raw, str):
        mtd_raw = mtd_raw.replace("%", "").strip()
    
    mtd_value = float(mtd_raw)
    
    return nav_value, mtd_value
