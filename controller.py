import os
import re
import pandas as pd
import pdfplumber

folder_path = r"C:\YourFolderPath"  # change this


# ==============================
# MAIN PROCESSING LOOP
# ==============================

results = []

for file in os.listdir(folder_path):
    
    file_path = os.path.join(folder_path, file)
    
    # ------------------------------
    # 1️⃣ ORBIS PDFs
    # ------------------------------
    if file.lower().endswith(".pdf"):
        
        fund_code = re.sub(r"\s*\.pdf$", "", file, flags=re.IGNORECASE)
        
        nav, mtd = extract_nav_mtd_from_pdf(file_path, file)
        
        results.append({
            "fund_code_extract": fund_code,
            "NAV": nav,
            "MTD": mtd
        })
    
    
    # ------------------------------
    # 2️⃣ ALLAN GRAY BALANCED EXCEL
    # ------------------------------
    elif file.lower().endswith((".xls", ".xlsx")):
        
        normalized = file.lower()
        
        if all(k in normalized for k in ["allan", "gray", "balanced"]):
            
            nav, mtd = extract_alan_gray_balanced(file_path)
            
            results.append({
                "fund_code_extract": "AllanGrayAustraliaBalancedFund",
                "NAV": nav,
                "MTD": mtd
            })


# ==============================
# FINAL OUTPUT
# ==============================

final_df = pd.DataFrame(results)
print(final_df)
