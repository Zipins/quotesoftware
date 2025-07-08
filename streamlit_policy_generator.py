import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

# 页面设置
st.set_page_config(page_title="保单生成器", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote PDF 或图片（PNG/JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split(".")[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # 创建 Textract 客户端
    textract = boto3.client(
        "textract",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_REGION"]
    )

    # 根据文件类型选择 Textract 模式
    try:
        with open(tmp_path, "rb") as doc:
            file_bytes = doc.read()

        if uploaded_file.type == "application/pdf":
            response = textract.analyze_document(
                Document={"Bytes": file_bytes},
                FeatureTypes=["TABLES", "FORMS"]
            )
        elif uploaded_file.type.startswith("image/"):
            response = textract.detect_document_text(
                Document={"Bytes": file_bytes}
            )
        else:
            st.error("❌ 文件格式不被支持，请上传扫描型 PDF 或清晰图片（PNG/JPG）。")
            st.stop()

        # 识别文本行
        lines = [item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]
        extracted_text = "\n".join(lines)

    except Exception as e:
        st.error(f"❌ Textract 识别失败：{str(e)}")
        st.stop()
    finally:
        os.remove(tmp_path)

    # 显示原始识别文本
    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 结构化解析
    quote_data = parse_quote_from_text(extracted_text)

    # 生成保单
    output_path = generate_policy_doc(quote_data)

    # 提供下载按钮
    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
