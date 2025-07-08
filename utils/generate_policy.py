from docx import Document
import os
import tempfile

def generate_policy_doc(data: dict) -> str:
    template_path = "template/保单范例.docx"
    doc = Document(template_path)

    # 责任险
    if data.get("liability_selected"):
        doc.tables[0].cell(1, 1).text = "✅"
        doc.tables[0].cell(1, 2).text = f"赔偿对方身体伤害 ${data['liability_per_person']}/人，事故最多 ${data['liability_per_accident']}"
    else:
        doc.tables[0].cell(1, 1).text = "❌"
        doc.tables[0].cell(1, 2).text = "没有选择该项目"

    # 无保险驾驶者
    if data.get("uninsured_motorist_selected"):
        doc.tables[0].cell(2, 1).text = "✅"
        doc.tables[0].cell(2, 2).text = f"赔偿你和乘客医疗费 ${data['umbip_per_person']}/人，一场事故最多 ${data['umbip_per_accident']}"
    else:
        doc.tables[0].cell(2, 1).text = "❌"
        doc.tables[0].cell(2, 2).text = "没有选择该项目"

    # 医疗费用
    if data.get("medical_payment_selected"):
        doc.tables[0].cell(3, 1).text = "✅"
        doc.tables[0].cell(3, 2).text = f"赔偿自己和自己车上乘客在事故中受伤的医疗费每人 ${data['medical_payment_amount']}"
    else:
        doc.tables[0].cell(3, 1).text = "❌"
        doc.tables[0].cell(3, 2).text = "没有选择该项目"

    # PIP
    if data.get("pip_selected"):
        doc.tables[0].cell(4, 1).text = "✅"
        doc.tables[0].cell(4, 2).text = f"赔偿自己和自己车上乘客在事故中受伤的医疗费，误工费和精神损失费每人 ${data['pip_amount']}"
    else:
        doc.tables[0].cell(4, 1).text = "❌"
        doc.tables[0].cell(4, 2).text = "没有选择该项目"

    # 输出临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        return tmp.name
