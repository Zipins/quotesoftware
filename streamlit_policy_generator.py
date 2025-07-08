import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_docx

st.set_page_config(page_title="中文保单生成系统", page_icon="📄", layout="centered")

st.markdown("## 中文保单生成系统")
st.markdown("上传保险 Quote PDF 或图片（PNG/JPG）")

# 获取 AWS Textract 客户端
aws_access_key_id = st.secrets["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]
aws_region = st.secrets["AWS_REGION"]
textract = boto3.client(
    "textract",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
)

uploaded_file = st.file_uploader("上传文件", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"上传成功：{uploaded_file.name}")
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    try:
        # 判断文件类型
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext in [".png", ".jpg", ".jpeg"]:
            with open(tmp_file_path, "rb") as doc:
                response = textract.detect_document_text(Document={"Bytes": doc.read()})
                st.write(response)  # ✅ debug 打印出来看看
        elif ext == ".pdf":
            with open(tmp_file_path, "rb") as doc:
                response = textract.analyze_document(
                    Document={"Bytes": doc.read()},
                    FeatureTypes=["FORMS"],
                )
                st.write(response)  # ✅ debug 打印 PDF 返回结果
        else:
            st.error("❌ 文件格式不被支持，请上传扫描型 PDF 或清晰图片（PNG/JPG）。")
            os.unlink(tmp_file_path)
            st.stop()

        # 提取文字
        blocks = response.get("Blocks", [])
        text_blocks = [b["Text"] for b in blocks if b["BlockType"] == "LINE" and "Text" in b]
        extracted_text = "\n".join(text_blocks)

        if not extracted_text.strip():
            st.error("❌ Textract 识别失败：未检测到任何文本。请确认文件为清晰扫描件。")
            os.unlink(tmp_file_path)
            st.stop()

        st.success("✅ Textract 识别成功，正在生成保单...")

        parsed_data = parse_quote_from_text(extracted_text)
        docx_path = generate_policy_docx(parsed_data)

        with open(docx_path, "rb") as f:
            st.download_button("📥 点击下载生成的中文保单", f, file_name="中文保单.docx")

        os.unlink(docx_path)
        os.unlink(tmp_file_path)

    except Exception as e:
        st.error(f"❌ Textract 识别失败：{str(e)}")
        os.unlink(tmp_file_path)
