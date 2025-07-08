import re

def parse_quote_from_text(text: str) -> dict:
    # 提取责任险（Liability）
    liability_match = re.search(r'Liability\s*:\s*\$?([\d,]+)[/$](\$?[\d,]+)', text, re.IGNORECASE)
    liability = {
        "selected": bool(liability_match),
        "per_person": liability_match.group(1).replace(",", "") if liability_match else "",
        "per_accident": liability_match.group(2).replace(",", "") if liability_match else ""
    }

    # Medical Payments
    med_match = re.search(r'Medical\s+Payments\s*.*?\$([\d,]+)', text, re.IGNORECASE)
    medical_payment = {
        "selected": bool(med_match),
        "amount": med_match.group(1).replace(",", "") if med_match else ""
    }

    # Personal Injury Protection
    pip_match = re.search(r'Personal\s+Injury\s+Protection\s*.*?\$([\d,]+)', text, re.IGNORECASE)
    personal_injury = {
        "selected": bool(pip_match),
        "amount": pip_match.group(1).replace(",", "") if pip_match else ""
    }

    # Uninsured Motorist Bodily Injury
    umbi_match = re.search(r'UMBI.*?\$([\d,]+)[/$](\$[\d,]+)', text, re.IGNORECASE)
    # Uninsured Motorist Property Damage
    umpd_match = re.search(r'UMPD.*?\$([\d,]+).*?(Deductible[:：]?\s*\$([\d,]+))?', text, re.IGNORECASE)
    uninsured_motorist = {
        "umb_selected": bool(umbi_match),
        "umbi_per_person": umbi_match.group(1).replace(",", "") if umbi_match else "",
        "umbi_per_accident": umbi_match.group(2).replace(",", "") if umbi_match else "",
        "umpd_selected": bool(umpd_match),
        "umpd_amount": umpd_match.group(1).replace(",", "") if umpd_match else "",
        "umpd_deductible": umpd_match.group(3).replace(",", "") if umpd_match and umpd_match.group(3) else "250"
    }

    # 车辆信息（示例）
    vehicles = []
    vin_matches = re.findall(r'(?:VIN[:：]?\s*)([A-HJ-NPR-Z0-9]{17})', text)
    for vin in vin_matches:
        vehicles.append({
            "vin": vin,
            "year_make_model": "Unknown",
            "collision": {"selected": False},
            "comprehensive": {"selected": False},
            "roadside": {"selected": False},
            "rental": {"selected": False}
        })

    return {
        "liability": liability,
        "medical_payment": medical_payment,
        "personal_injury": personal_injury,
        "uninsured_motorist": uninsured_motorist,
        "vehicles": vehicles
    }
