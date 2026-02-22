import pandas as pd
import numpy as np
import re


def extract_alan_gray_balanced(file_path):
    """
    Extract NAV and MTD from Allan Gray Australia Balanced Fund Excel file.
    
    NAV  -> Last monthly value from 'Total Fund Size (A$m)' converted to full number.
    MTD  -> Last monthly value from 'Net' column (in percent units, e.g., 0.35).
    """

    # -------------------------------------------------
    # 1️⃣ Load raw file (no header assumption)
    # -------------------------------------------------
    df_raw = pd.read_excel(file_path, header=None)

    # -------------------------------------------------
    # 2️⃣ Find header row dynamically
    # -------------------------------------------------
    header_row = None

    for i, row in df_raw.iterrows():
        row_lower = row.astype(str).str.lower()
        if row_lower.str.contains("date").any() and row_lower.str.contains("total fund").any():
            header_row = i
            break

    if header_row is None:
        raise ValueError("Header row with DATE and Total Fund Size not found.")

    # -------------------------------------------------
    # 3️⃣ Read again using correct header
    # -------------------------------------------------
    df = pd.read_excel(file_path, header=header_row)

    # Clean column names (remove newlines & extra spaces)
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Validate required columns
    required_cols = ["DATE", "Net", "Total Fund Size (A$m)"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # -------------------------------------------------
    # 4️⃣ Convert DATE column to datetime
    # -------------------------------------------------
    df["DATE_dt"] = pd.to_datetime(df["DATE"], errors="coerce")

    # -------------------------------------------------
    # 5️⃣ Keep only the FIRST continuous block of real dates
    #      (This removes summary, FY, and calendar sections)
    # -------------------------------------------------
    monthly_rows = []
    started = False

    for idx, row in df.iterrows():
        if pd.notna(row["DATE_dt"]):
            monthly_rows.append(idx)
            started = True
        else:
            # Once we started collecting dates and hit first non-date,
            # stop (monthly section ended)
            if started:
                break

    if not monthly_rows:
        raise ValueError("No valid monthly date rows found.")

    df_monthly = df.loc[monthly_rows].copy()

    # -------------------------------------------------
    # 6️⃣ Clean numeric columns safely
    # -------------------------------------------------

    # Total Fund Size (A$m)
    df_monthly["TotalFundSize_num"] = pd.to_numeric(
        df_monthly["Total Fund Size (A$m)"], errors="coerce"
    )

    # Net column (handle % formatting or decimal storage)
    def clean_net(value):
        if pd.isna(value):
            return np.nan

        # If numeric (Excel percent stored as 0.0035)
        if isinstance(value, (int, float)):
            if abs(value) < 1:
                return value * 100
            return value

        # If string like "0.35%"
        value = str(value).replace("%", "").strip()
        return float(value)

    df_monthly["Net_num"] = df_monthly["Net"].apply(clean_net)

    # Remove rows with missing NAV or Net
    df_monthly = df_monthly[
        df_monthly["TotalFundSize_num"].notna() &
        df_monthly["Net_num"].notna()
    ]

    if df_monthly.empty:
        raise ValueError("No valid monthly rows with NAV and Net found.")

    # -------------------------------------------------
    # 7️⃣ Pick last monthly date
    # -------------------------------------------------
    df_monthly = df_monthly.sort_values("DATE_dt")
    last_row = df_monthly.iloc[-1]

    # -------------------------------------------------
    # 8️⃣ Final Values
    # -------------------------------------------------
    nav_value = float(last_row["TotalFundSize_num"]) * 1_000_000
    mtd_value = float(last_row["Net_num"])

    return nav_value, mtd_value
