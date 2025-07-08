import re

def parse_quote_from_text(text: str) -> dict:
    data = {}

    # 责任险（Liability）
    liability_match = re.search(r'Bodily Injury\s*\$([\d,]+)\s*/\s*\$([\d,]+)', text)
    if liability_match:
        data["liability_selected"] = True
        data["liability_per_person"] = liability_match.group(1)
        data["liability_per_accident"] = liability_match.group(2)
    else:
        data["liability_selected"] = False

    # 无保险驾驶者（Uninsured Motorist Bodily Injury）
    umbi_match = re.search(r'Uninsured Motorist.*?\$([\d,]+)\s*/\s*\$([\d,]+)', text)
    if umbi_match:
        data["uninsured_motorist_selected"] = True
        data["umbip_per_person"] = umbi_match.group(1)
        data["umbip_per_accident"] = umbi_match.group(2)
    else:
        data["uninsured_motorist_selected"] = False

    # 医疗费用（Medical Payments）
    med_match = re.search(r'Medical Payments.*?\$([\d,]+)', text)
    if med_match:
        data["medical_payment_selected"] = True
        data["medical_payment_amount"] = med_match.group(1)
    else:
        data["medical_payment_selected"] = False

    # 人身伤害保护（Personal Injury Protection / PIP）
    pip_match = re.search(r'Personal Injury Protection.*?\$([\d,]+)', text)
    if pip_match:
        data["pip_selected"] = True
        data["pip_amount"] = pip_match.group(1)
    else:
        data["pip_selected"] = False

    return data
