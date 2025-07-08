import re

def parse_quote_from_text(text):
    result = {
        "liability": {"selected": False, "bodily": 0, "property": 0},
        "uninsured_motorist": {"selected": False, "bodily_per_person": 0, "bodily_per_accident": 0, "property": 0, "deductible": 250},
        "medical_payment": {"selected": False, "amount": 0},
        "personal_injury": {"selected": False, "amount": 0},
        "vehicles": [],
    }

    def extract_amount(pattern, default=0):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amt = match.group(1).replace(",", "")
            return int(amt)
        return default

    # Liability
    if "liability" in text.lower():
        result["liability"]["selected"] = True
        result["liability"]["bodily"] = extract_amount(r"(\d{1,3},?\d{3})\s*/\s*\d{1,3},?\d{3}")
        result["liability"]["property"] = extract_amount(r"property damage.*?\$?(\d{1,3},?\d{3})")

    # Uninsured Motorist
    if "uninsured" in text.lower():
        result["uninsured_motorist"]["selected"] = True
        result["uninsured_motorist"]["bodily_per_person"] = extract_amount(r"uninsured.*?(\d{1,3},?\d{3})\s*/", 0)
        result["uninsured_motorist"]["bodily_per_accident"] = extract_amount(r"uninsured.*?/\s*(\d{1,3},?\d{3})", 0)
        result["uninsured_motorist"]["property"] = extract_amount(r"uninsured.*property.*?\$?(\d{1,3},?\d{3})", 0)

    # Med Pay
    if re.search(r"med(ical)?\s*pay", text, re.IGNORECASE):
        result["medical_payment"]["selected"] = True
        result["medical_payment"]["amount"] = extract_amount(r"med(ical)?\s*pay.*?\$?(\d{1,3},?\d{3})")

    # Personal Injury Protection
    if "personal injury" in text.lower():
        result["personal_injury"]["selected"] = True
        result["personal_injury"]["amount"] = extract_amount(r"personal injury.*?\$?(\d{1,3},?\d{3})")

    # Vehicle coverages
    vehicle_pattern = re.compile(
        r"(\d{4})\s+([A-Z0-9 ]+)\s+VIN[:：]?\s*([A-Z0-9]+).*?"
        r"collision.*?\$?(\d{1,3},?\d{3}).*?"
        r"comprehensive.*?\$?(\d{1,3},?\d{3})", re.IGNORECASE | re.DOTALL)
    for match in vehicle_pattern.finditer(text):
        year, model, vin, collision, comp = match.groups()
        result["vehicles"].append({
            "year": year,
            "model": model.strip(),
            "vin": vin,
            "collision": int(collision.replace(",", "")),
            "comprehensive": int(comp.replace(",", "")),
            "rental": extract_amount(r"rental.*?\$?(\d+)", 0),
            "roadside": extract_amount(r"roadside.*?\$?(\d+)", 0),
        })

    return result
