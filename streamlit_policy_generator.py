import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

st.set_page_config(page_title="保单生成器", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote PDF 文件", type=["pdf"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 创建 AWS Textract 客户端（从 secrets 中读取凭证）
    textract = boto3.client(
        "textract",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )

    # 将 PDF 保存为临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_pdf_path = tmp_file.name

    # 读取 PDF 文件并调用 Textract
    with open(tmp_pdf_path, "rb") as doc:
        try:
            response = textract.detect_document_text(Document={"Bytes": doc.read()})
        except Exception as e:
            st.error(f"❌ Textract 识别失败：{str(e)}")
            st.stop()

    # 提取文字内容
    extracted_text = "\n".join([
        item["DetectedText"]
        for item in response["Blocks"]
        if item["BlockType"] == "LINE"
    ])

    # 显示原始文本（可折叠）
    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 结构化提取 quote 信息
    quote_data = parse_quote_from_text(extracted_text)

    # 生成中文保单 Word 文件
    output_path = generate_policy_doc(quote_data)

    # 提供下载按钮
    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # 清理临时文件
    os.remove(tmp_pdf_path)
