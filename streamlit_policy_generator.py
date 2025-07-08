import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

st.set_page_config(page_title="保单生成器", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote 文件（支持 PDF / PNG / JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 创建 Textract 客户端，使用 secrets.toml 中的凭证
    textract = boto3.client(
        "textract",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_REGION"]
    )

    # 保存为临时文件
    suffix = "." + uploaded_file.name.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # 判断文件类型是否支持
    if suffix.lower() not in [".png", ".jpg", ".jpeg", ".pdf"]:
        st.error("❌ 文件格式不被支持，请上传扫描型 PDF 或清晰图片（PNG/JPG）。")
        st.stop()

    # 读取文件内容并调用 Textract
    with open(tmp_path, "rb") as f:
        try:
            response = textract.detect_document_text(Document={"Bytes": f.read()})
        except Exception as e:
            st.error(f"❌ Textract 识别失败：{str(e)}")
            st.stop()

    # 安全提取文字内容（避免 KeyError）
    extracted_text = "\n".join([
        item["DetectedText"]
        for item in response.get("Blocks", [])
        if item.get("BlockType") == "LINE" and "DetectedText" in item
    ])

    # 显示识别结果
    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 提取结构化 quote 数据
    quote_data = parse_quote_from_text(extracted_text)

    # 生成中文保单文档
    output_path = generate_policy_doc(quote_data)

    # 下载按钮
    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # 清理
    os.remove(tmp_path)
