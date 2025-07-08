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

    # 创建 AWS Textract 客户端
    textract = boto3.client(
        "textract",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )

    # 保存上传文件为临时文件
    suffix = "." + uploaded_file.name.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    with open(tmp_path, "rb") as doc:
        try:
            if suffix.lower() in [".png", ".jpg", ".jpeg"]:
                response = textract.detect_document_text(Document={"Bytes": doc.read()})
            elif suffix.lower() == ".pdf":
                response = textract.analyze_document(
                    Document={"Bytes": doc.read()},
                    FeatureTypes=["TABLES", "FORMS"]
                )
            else:
                st.error("❌ 文件格式不被支持，请上传 PDF 或图片（PNG/JPG）。")
                st.stop()

            # 👇👇👇 加入调试信息 👇👇👇
            st.write("🧪 Textract 原始响应：", response)

        except Exception as e:
            st.error(f"❌ Textract 识别失败：{str(e)}")
            st.stop()

    # 提取识别文字内容（只支持 detect_document_text）
    if "Blocks" not in response:
        st.error("❌ 未检测到文档内容，请上传更清晰的扫描件或图片。")
        st.stop()

    extracted_text = "\n".join([
        item["DetectedText"]
        for item in response["Blocks"]
        if item["BlockType"] == "LINE" and "DetectedText" in item
    ])

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

    os.remove(tmp_path)
