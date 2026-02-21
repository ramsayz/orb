import os
import re
import pandas as pd
import pdfplumber

folder_path = r"C:\YourFolderPath"  # change this

def norm(s: str) -> str:
    # lowercase, remove extension, remove ALL non-alphanumeric (spaces, dashes, underscores, extra dots)
    s = s.lower().strip()
    s = re.sub(r"\.pdf$", "", s)              # remove .pdf if present
    s = re.sub(r"\.xlsx?$|\.xls$", "", s)     # remove excel extensions if present
    s = re.sub(r"[^a-z0-9]+", "", s)          # remove spaces/symbols
    return s

def base_name_no_ext(filename: str) -> str:
    # robustly remove extension even if there is a space before .pdf
    f = filename.strip()
    f = re.sub(r"\s*\.pdf$", "", f, flags=re.IGNORECASE)
    f = re.sub(r"\s*\.xlsx?$|\s*\.xls$", "", f, flags=re.IGNORECASE)
    return f.strip()

# ✅ YOUR selected PDFs (use exactly what you want to process)
selected_pdfs = [
    "OrbisFactSheetSICAVGlobalBalanced .pdf",
    "OrbisFactSheetOEICGlobalBalanced .pdf",
    "OrbisFactSheetOEICGlobalCautious .pdf",
    "OrbisFactSheetOptimalLP .pdf",
    "OrbisFactSheetOptimalDollar .pdf",
    "OrbisFactSheetSICAVGlobalCautiousSharedRfbMdd .pdf",
]

# Normalize selected list for matching
selected_norm_set = {norm(x) for x in selected_pdfs}

results = []
files = os.listdir(folder_path)

# ---- PDFs: read only selected ----
for f in files:
    if f.lower().endswith(".pdf") or re.search(r"\.pdf\s*$", f.lower()):
        if norm(f) in selected_norm_set:
            path = os.path.join(folder_path, f)

            with pdfplumber.open(path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        full_text += t + "\n"

            # fund_code_extract = file name (no extension)
            results.append({
                "fund_code_extract": base_name_no_ext(f),
                "source_type": "PDF",
                "matched_file_name": f,
                "raw_text_length": len(full_text)  # placeholder for now
            })

# ---- Alan Gray Excel: keyword match + pick latest ----
alan_candidates = []
for f in files:
    if f.lower().endswith((".xls", ".xlsx")):
        n = norm(f)
        if all(k in n for k in ["allangray", "australia", "equity", "fund"]):
            full_path = os.path.join(folder_path, f)
            alan_candidates.append((f, full_path, os.path.getmtime(full_path)))

if alan_candidates:
    f, path, _ = max(alan_candidates, key=lambda x: x[2])  # latest modified
    df_x = pd.read_excel(path)

    results.append({
        "fund_code_extract": "Allan Gray Australia Equity Fund",
        "source_type": "EXCEL",
        "matched_file_name": f,
        "rows_in_excel": len(df_x)  # placeholder for now
    })

final_df = pd.DataFrame(results)
print(final_df)
