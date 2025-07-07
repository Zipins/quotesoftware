import streamlit as st
import boto3
import tempfile
import os
from docx import Document
from quote_parser import parse_quote_from_text, generate_chinese_description, fill_template_with_data

# 设置页面标题
st.set_page_config(page_title="保单生成系统")

st.title("保单生成系统")
st.write("欢迎使用保单自动生成工具。请上传报价 PDF 文件。")

# 上传 PDF 文件
uploaded_file = st.file_uploader("上传报价 PDF 文件", type=["pdf"])

if uploaded_file:
    st.success(f"上传成功！文件名：{uploaded_file.name}")

    # 保存 PDF 文件到临时路径
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_file.read())
        tmp_pdf_path = tmp_pdf.name

    # 用 AWS Textract 做 OCR 识别
    textract = boto3.client(
        "textract",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION")
    )

    with open(tmp_pdf_path, "rb") as doc:
        response = textract.detect_document_text(Document={'Bytes': doc.read()})

    # 提取文字内容
    extracted_text = "\n".join(
        [item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]
    )

    st.subheader("识别结果预览")
    st.text_area("以下是从报价文件中提取的文本内容：", extracted_text, height=300)

    # 解析保单内容
    st.subheader("正在生成保单内容...")
    raw_data = parse_quote_from_text(extracted_text)
    filled_doc = fill_template_with_data(raw_data)

    # 保存生成的 Word 文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
        filled_doc.save(tmp_docx.name)
        download_path = tmp_docx.name

    # 下载按钮
    with open(download_path, "rb") as f:
        st.download_button(
            label="点击下载生成的中文保单文件",
            data=f,
            file_name="生成保单.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
