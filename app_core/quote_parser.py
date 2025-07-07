from app_core.ocr import extract_text_from_pdf
from app_core.parsing import parse_quote_from_text
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
    result = {}

    if parsed_data.get('liability_selected'):
        result['liability'] = (
            f"✅\n赔偿他人身体伤害：${parsed_data.get('liability_bodily')}\n"
            f"赔偿他人财产损失：${parsed_data.get('liability_property')}"
        )
    else:
        result['liability'] = "❌\n没有选择该项目"

    # 可继续添加其他字段的说明
    return result
