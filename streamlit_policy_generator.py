import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

st.set_page_config(page_title="保单生成器", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote 文件（PDF、PNG、JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 创建 Textract 客户端
    textract = boto3.client(
        "textract",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )

    # 保存临时文件
    suffix = "." + uploaded_file.name.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    try:
        with open(tmp_path, "rb") as doc:
            if suffix in [".png", ".jpg", ".jpeg"]:
                response = textract.detect_document_text(Document={"Bytes": doc.read()})
            elif suffix == ".pdf":
                response = textract.analyze_document(
                    Document={"Bytes": doc.read()},
                    FeatureTypes=["TABLES", "FORMS"]
                )
            else:
                st.error("❌ 文件格式不支持，请上传 PDF 或 PNG/JPG。")
                st.stop()
    except Exception as e:
        st.error(f"❌ Textract 识别失败：{str(e)}")
        os.remove(tmp_path)
        st.stop()

    if "Blocks" not in response:
        st.error("❌ 没有识别结果，请上传清晰的扫描件或截图。")
        os.remove(tmp_path)
        st.stop()

    lines = []
    for block in response["Blocks"]:
        if block.get("BlockType") == "LINE" and "DetectedText" in block:
            lines.append(block["DetectedText"])

    if not lines:
        st.error("❌ 没有识别出任何文字，请尝试更清晰的图片或 PDF。")
        os.remove(tmp_path)
        st.stop()

    extracted_text = "\n".join(lines)

    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 提取 quote 信息
    quote_data = parse_quote_from_text(extracted_text)

    # 生成中文保单
    output_path = generate_policy_doc(quote_data)

    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    os.remove(tmp_path)
