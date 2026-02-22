# Convert DATE column safely
df["DATE_dt"] = pd.to_datetime(df["DATE"], errors="coerce")

# Keep only rows that are real monthly dates
df_monthly = df[df["DATE_dt"].notna()].copy()

# IMPORTANT: Monthly table is the first continuous block of dates
# Stop once DATE becomes NaT (summary section starts)

first_invalid_index = df["DATE_dt"].isna().idxmax()

if first_invalid_index > 0:
    df_monthly = df.loc[:first_invalid_index - 1].copy()
    df_monthly["DATE_dt"] = pd.to_datetime(df_monthly["DATE"], errors="coerce")
    df_monthly = df_monthly[df_monthly["DATE_dt"].notna()]

# Now sort safely
df_monthly = df_monthly.sort_values("DATE_dt")

last_row = df_monthly.iloc[-1]
