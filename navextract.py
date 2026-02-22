# -------- NAV --------
nav_pattern = rf"{nav_keyword}\s+.*?([\d,\.]+\s*(million|billion|thousand))"

nav_match = re.search(nav_pattern, full_text, re.IGNORECASE)

if nav_match:
    nav_raw = nav_match.group(1)
    nav_value = convert_money_string(nav_raw)
else:
    nav_value = None
