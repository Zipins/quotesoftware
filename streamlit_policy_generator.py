import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

# 设置页面标题
st.set_page_config(page_title="中文保单生成系统")

st.title("📄 中文保单生成系统")
st.markdown("上传保险 Quote PDF 或图片（PNG/JPG）")

# 上传文件
uploaded_file = st.file_uploader("上传保险 Quote PDF 或图片（PNG/JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"上传成功：{uploaded_file.name}")

    # 将上传文件保存为临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    try:
        # 判断文件类型
        file_ext = uploaded_file.name.lower().split('.')[-1]
        textract = boto3.client(
            "textract",
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["AWS_REGION"]
        )

        # 自动选择 Textract 接口
        if file_ext in ["png", "jpg", "jpeg"]:
            with open(tmp_file_path, 'rb') as document:
                image_bytes = document.read()
            response = textract.detect_document_text(Document={'Bytes': image_bytes})
        elif file_ext == "pdf":
            with open(tmp_file_path, 'rb') as document:
                pdf_bytes = document.read()
            response = textract.analyze_document(
                Document={'Bytes': pdf_bytes},
                FeatureTypes=["FORMS"]
            )
        else:
            st.error("❌ 不支持的文件格式，请上传 PDF 或图片")
            raise ValueError("Unsupported file type")

        # 提取文本
        blocks = response.get("Blocks", [])
        all_text = "\n".join([block["Text"] for block in blocks if block["BlockType"] == "LINE"])

        if not all_text.strip():
            st.error("❌ Textract 识别失败：没有检测到文字内容")
        else:
            # 解析 quote 信息
            parsed_data = parse_quote_from_text(all_text)

            # 生成中文保单
            output_path = generate_policy_doc(parsed_data)

            with open(output_path, "rb") as f:
                st.download_button("📥 下载生成的中文保单", f, file_name="中文保单.docx")

    except Exception as e:
        st.error(f"❌ Textract 识别失败：{str(e)}")

    finally:
        os.remove(tmp_file_path)
