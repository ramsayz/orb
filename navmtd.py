import os
import re
import pandas as pd
import pdfplumber

folder_path = r"C:\YourFolderPath"  # change this


# -------- MONEY CONVERTER --------
def convert_money_string(value):
    if not value:
        return None
    
    value = value.replace(",", "").lower()
    
    multiplier = 1
    if "billion" in value:
        multiplier = 1_000_000_000
    elif "million" in value:
        multiplier = 1_000_000
    elif "thousand" in value:
        multiplier = 1_000
    
    number = re.findall(r"[-+]?\d*\.?\d+", value)
    if not number:
        return None
    
    return float(number[0]) * multiplier


# -------- EXTRACT FUNCTION --------
def extract_nav_mtd_from_pdf(pdf_path, file_name):
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    # ---------- SPECIAL CASE ----------
    if file_name.lower() == "orbisfactsheetasadollarmdd.pdf":
        nav_keyword = "Class size"
    else:
        nav_keyword = "Fund size"
    
    
    # -------- NAV --------
    nav_pattern = rf"{nav_keyword}\s+US\$?([\d,\.]+\s*(million|billion|thousand)?)"
    nav_match = re.search(nav_pattern, full_text, re.IGNORECASE)
    
    if nav_match:
        nav_raw = nav_match.group(1)
        nav_value = convert_money_string(nav_raw)
    else:
        nav_value = None
    
    
    # -------- MTD (1 month) --------
    mtd_match = re.search(r"1\s*month\s+([-+]?\d*\.?\d+)", full_text, re.IGNORECASE)
    
    if mtd_match:
        mtd_value = float(mtd_match.group(1))
    else:
        mtd_value = None
    
    return nav_value, mtd_value


# -------- MAIN LOOP --------
results = []

for file in os.listdir(folder_path):
    if file.lower().endswith(".pdf"):
        
        pdf_path = os.path.join(folder_path, file)
        fund_code = re.sub(r"\s*\.pdf$", "", file, flags=re.IGNORECASE)
        
        nav, mtd = extract_nav_mtd_from_pdf(pdf_path, file)
        
        results.append({
            "fund_code_extract": fund_code,
            "NAV": nav,
            "MTD": mtd
        })

final_df = pd.DataFrame(results)
print(final_df)
