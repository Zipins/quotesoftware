import streamlit as st
import boto3
import tempfile
import os
from docx import Document
from app_core.parsing import parse_quote_from_text, generate_chinese_description
from app_core.word_writer import write_policy_to_word

# 设置页面标题
st.set_page_config(page_title="保单生成系统")

# 正确读取 Word 模板路径
template_path = os.path.join(os.path.dirname(__file__), "保单范例.docx")

# 设置标题
st.title("📄 保险保单生成工具")

# 文件上传
uploaded_file = st.file_uploader("上传保险报价 PDF 文件", type=["pdf"])

if uploaded_file is not None:
    st.success(f"上传成功！文件名：{uploaded_file.name}")

    # 创建 AWS Textract 客户端
    textract = boto3.client("textract", region_name=os.getenv("AWS_REGION"))

    # 将上传的 PDF 读取为二进制
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # 调用 Textract OCR 提取文本
    with open(tmp_path, "rb") as doc:
        response = textract.detect_document_text(Document={"Bytes": doc.read()})

    # 提取 OCR 中的文字内容
    extracted_text = "\n".join([item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"])

    # 解析报价内容
    parsed_data = parse_quote_from_text(extracted_text)

    # 生成中文说明
    enriched_data = generate_chinese_description(parsed_data)

    # 创建输出文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_out:
        output_path = tmp_out.name
        write_policy_to_word(enriched_data, template_path, output_path)

    # 提供下载
    with open(output_path, "rb") as f:
        st.download_button("📥 下载生成的中文保单", f, file_name="生成保单.docx")

