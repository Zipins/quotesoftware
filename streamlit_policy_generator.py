import streamlit as st
import boto3
import os
import tempfile
import traceback
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_docx

st.set_page_config(page_title="中文保单生成系统")

st.title("📄 中文保单生成系统")
st.markdown("上传保险 Quote PDF 或图片（PNG/JPG）")

uploaded_file = st.file_uploader("上传保险 Quote 文件：", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 将上传的文件保存到临时文件夹
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    try:
        # 判断是文本 PDF 还是扫描件/图片
        if uploaded_file.type == "application/pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(tmp_file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if len(text.strip()) > 20:
                st.success("✅ 识别为文本型 PDF，开始解析内容...")
                quote_data = parse_quote_from_text(text)
            else:
                st.warning("🤖 检测为扫描型 PDF，使用 Textract OCR 识别...")
                textract = boto3.client(
                    'textract',
                    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
                    region_name=st.secrets["AWS_DEFAULT_REGION"]
                )
                with open(tmp_file_path, "rb") as document:
                    imageBytes = document.read()
                response = textract.detect_document_text(Document={'Bytes': imageBytes})

                detected_text = "\n".join([item["DetectedText"] for item in response["Blocks"] if item["BlockType"] == "LINE"])
                if not detected_text.strip():
                    raise ValueError("Textract 返回为空或未能识别任何文字")
                quote_data = parse_quote_from_text(detected_text)

        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            st.info("📷 上传为图片，将使用 Textract 识别内容...")
            textract = boto3.client(
                'textract',
                aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
                region_name=st.secrets["AWS_DEFAULT_REGION"]
            )
            with open(tmp_file_path, "rb") as document:
                imageBytes = document.read()
            response = textract.detect_document_text(Document={'Bytes': imageBytes})

            detected_text = "\n".join([item["DetectedText"] for item in response["Blocks"] if item["BlockType"] == "LINE"])
            if not detected_text.strip():
                raise ValueError("Textract 返回为空或未能识别任何文字")
            quote_data = parse_quote_from_text(detected_text)

        else:
            st.error("❌ 文件格式不被支持，请上传 PDF 或 PNG/JPG 图片。")
            st.stop()

        # 调用生成函数
        output_path = generate_policy_docx(quote_data)

        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 下载生成的中文保单",
                data=f,
                file_name="中文保单.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    except Exception as e:
        st.error(f"❌ Textract 识别失败：{str(e)}")
        st.code(traceback.format_exc(), language="python")
