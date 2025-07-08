import re

def parse_quote_from_text(text):
    def extract_amount(pattern):
        match = re.search(pattern, text)
        return match.group(1).replace(',', '') if match else None

    def is_selected(keyword):
        return keyword.lower() in text.lower() and re.search(r"\$\s*\d+", text)

    data = {
        "liability": {
            "selected": bool(re.search(r"Liability", text, re.IGNORECASE)),
            "bodily_injury": extract_amount(r"Liability.*?(\d{1,3},?\d{3}/\d{1,3},?\d{3})"),
            "property_damage": extract_amount(r"Property Damage.*?(\d{1,3},?\d{3})"),
        },
        "uninsured_motorist": {
            "selected": "Uninsured" in text or "Underinsured" in text,
            "bodily_injury": extract_amount(r"Unins.*?(\d{1,3},?\d{3}/\d{1,3},?\d{3})"),
            "property_damage": extract_amount(r"Unins.*?Motorists PD.*?(\d{1,3},?\d{3})"),
            "property_deductible": extract_amount(r"UMPD.*?\$?(\d{1,3}) Deductible")
        },
        "medical_payment": {
            "selected": is_selected("Medical Payments") or is_selected("Med Pay"),
            "limit": extract_amount(r"Med(ical)? (Payments|Pay).*?(\d{1,3},?\d{3})")
        },
        "personal_injury": {
            "selected": is_selected("Personal Injury Protection") or is_selected("PIP"),
            "limit": extract_amount(r"PIP.*?\$?(\d{1,3},?\d{3})")
        },
        "vehicles": []
    }

    vehicle_blocks = re.findall(r"(\d{4}.*?)TOTAL PER VEHICLE", text, re.DOTALL)
    for block in vehicle_blocks:
        vehicle_info = re.search(r"(\d{4}.*?)\n", block)
        vehicle_name = vehicle_info.group(1).strip() if vehicle_info else "Unknown"
        vin_match = re.search(r"VIN[:：]?\s*([A-HJ-NPR-Z0-9]{11,17})", block)
        vin = vin_match.group(1).strip() if vin_match else None

        def extract_vehicle_amount(label):
            m = re.search(rf"{label}.*?\$(\d{1,3}(,\d{3})*\.?\d*)", block)
            return m.group(1).replace(',', '') if m else None

        vehicle_data = {
            "name": vehicle_name,
            "vin": vin,
            "collision": extract_vehicle_amount("Collision"),
            "comprehensive": extract_vehicle_amount("Comprehensive"),
            "roadside": extract_vehicle_amount("Roadside"),
            "rental": extract_vehicle_amount("Rental")
        }
        data["vehicles"].append(vehicle_data)

    return data
