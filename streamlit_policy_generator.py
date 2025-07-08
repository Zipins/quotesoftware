import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

st.set_page_config(page_title="保单生成器", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote PDF 或图片（PNG/JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 保存上传文件为临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # 加载文件内容为二进制
    with open(tmp_file_path, "rb") as f:
        file_bytes = f.read()

    # 初始化 Textract 客户端（从 secrets 读取配置）
    try:
        textract = boto3.client(
            "textract",
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["AWS_DEFAULT_REGION"]
        )
    except Exception as e:
        st.error(f"❌ 无法创建 Textract 客户端，请检查配置：{str(e)}")
        st.stop()

    # 尝试识别文件内容
    try:
        response = textract.detect_document_text(Document={"Bytes": file_bytes})
        extracted_text = "\n".join([
            item["DetectedText"]
            for item in response["Blocks"]
            if item["BlockType"] == "LINE"
        ])
    except Exception as e:
        st.error(f"❌ Textract 识别失败：{str(e)}")
        st.stop()

    # 显示原始识别内容
    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 结构化信息抽取
    quote_data = parse_quote_from_text(extracted_text)

    # 生成中文保单
    output_path = generate_policy_doc(quote_data)

    # 提供下载链接
    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # 清理临时文件
    os.remove(tmp_file_path)
