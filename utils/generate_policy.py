from docx import Document
import os
import tempfile

def generate_policy_doc(data: dict) -> str:
    template_path = os.path.join("quotesoftware", "template", "保单范例.docx")
    doc = Document(template_path)

    # 示例：修改责任险
    for table in doc.tables:
        for row in table.rows:
            if "责任险（对方人身伤害/财产损失）" in row.cells[0].text:
                row.cells[1].text = "✅" if data["liability"]["selected"] else "❌"
                if data["liability"]["selected"]:
                    row.cells[2].text = f"赔偿对方人身伤害 ${data['liability']['per_person']}/人，事故总额最多 ${data['liability']['per_accident']}"
                else:
                    row.cells[2].text = "没有选择该项目"

    # 保存文件
    output_path = os.path.join(tempfile.gettempdir(), "保单说明.docx")
    doc.save(output_path)
    return output_path
