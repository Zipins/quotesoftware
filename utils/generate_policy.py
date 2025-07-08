from docx import Document
import tempfile
import os

def generate_policy_docx(data):
    template_path = "templates/保单范例.docx"
    doc = Document(template_path)

    # 填写责任险
    table = doc.tables[0]
    liability_row = table.rows[1].cells
    if data["liability"]["selected"]:
        liability_row[1].text = "✅"
        liability_row[2].text = f"赔偿他人伤亡 $ {data['liability']['bodily']}，财产损失 $ {data['liability']['property']}"
    else:
        liability_row[1].text = "❌"
        liability_row[2].text = "没有选择该项目"

    # 其他字段略，为简洁省略...

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        return tmp.name
