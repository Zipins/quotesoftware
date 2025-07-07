from app_core.ocr import extract_text_from_pdf
from app_core.parsing import parse_quote
from app_core.word_writer import write_policy_to_word

def parse_quote_from_text(text):
    # 将 OCR 提取出的文本，交给 parsing.py 处理
    return parse_quote(text)

def generate_chinese_description(parsed_data):
    """
    将解析后的数据 dict 转换成中文说明，用于填入保单 Word。
    parsed_data 应包含以下字段（示例）：
    {
        'liability_selected': True,
        'liability_bodily': '100,000/300,000',
        'liability_property': '100,000',
        ...
    }
    """
    description = {}

    if parsed_data.get("liability_selected"):
        description["责任险"] = f"""✅
赔偿对方车上人员身体伤害：${parsed_data['liability_bodily']}
赔偿对方车辆和财产损失：${parsed_data['liability_property']}"""
    else:
        description["责任险"] = "❌\n没有选择该项目"

    if parsed_data.get("uninsured_motorist_selected"):
        description["无保险驾驶者保障"] = f"""✅
赔偿你和乘客医疗费 ${parsed_data['um_bi_per_person']}/人
一场事故最多 ${parsed_data['um_bi_per_accident']}
赔偿自己车辆 ${parsed_data['um_pd_limit']}（自付额 ${parsed_data['um_pd_deductible']}）"""
    else:
        description["无保险驾驶者保障"] = "❌\n没有选择该项目"

    if parsed_data.get("medical_payment_selected"):
        description["医疗费用"] = f"""✅
赔偿自己和自己车上乘客在事故中受伤的医疗费每人${parsed_data['medical_payment_limit']}"""
    else:
        description["医疗费用"] = "❌\n没有选择该项目"

    if parsed_data.get("personal_injury_selected"):
        description["人身损失"] = f"""✅
赔偿自己和自己车上乘客在事故中受伤的医疗费，误工费和精神损失费每人${parsed_data['pip_limit']}"""
    else:
        description["人身损失"] = "❌\n没有选择该项目"

    return description
