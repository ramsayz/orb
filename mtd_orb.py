mtd_match = re.search(r"1\s*month\s+(\(?-?\d*\.?\d+\)?%?)", full_text, re.IGNORECASE)

if mtd_match:
    raw_value = mtd_match.group(1).replace("%", "")
    
    if raw_value.startswith("(") and raw_value.endswith(")"):
        mtd_value = -float(raw_value.strip("()"))
    else:
        mtd_value = float(raw_value)
else:
    mtd_value = None
