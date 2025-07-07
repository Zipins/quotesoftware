from app_core.ocr import extract_text_from_pdf
from app_core.word_writer import write_policy_to_word
from app_core.parsing import parse_quote  # ✅ 正确地引用 parse_quote 函数

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
    desc = {}

    if parsed_data.get("liability_selected"):
        desc["liability"] = f"""赔偿对方医疗费 ${parsed_data.get("liability_bodily")},
财产损失 ${parsed_data.get("liability_property")}"""
    else:
        desc["liability"] = "没有选择该项目"

    # ... 其他字段生成逻辑省略，可根据需要添加

    return desc
