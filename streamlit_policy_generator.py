import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

st.set_page_config(page_title="中文保单生成系统", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote PDF 或图片（PNG/JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 创建 Textract 客户端（从 secrets 读取）
    try:
        textract = boto3.client(
            "textract",
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["AWS_REGION"]
        )
    except Exception as e:
        st.error(f"❌ AWS Textract 配置失败：{e}")
        st.stop()

    # 临时保存文件
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # 调用 Textract 提取文字（根据文件类型判断 API）
    try:
        with open(tmp_path, "rb") as doc:
            if suffix.lower() == ".pdf":
                response = textract.analyze_document(
                    Document={"Bytes": doc.read()},
                    FeatureTypes=["TABLES", "FORMS"]
                )
            else:
                response = textract.detect_document_text(Document={"Bytes": doc.read()})
    except textract.exceptions.UnsupportedDocumentException:
        st.error("❌ 文件格式不被支持，请上传扫描型 PDF 或清晰图片（PNG/JPG）。")
        os.remove(tmp_path)
        st.stop()
    except Exception as e:
        st.error(f"❌ Textract 识别失败：{e}")
        os.remove(tmp_path)
        st.stop()

    # 提取文本内容
    try:
        lines = [block["DetectedText"] for block in response["Blocks"] if block["BlockType"] == "LINE"]
        extracted_text = "\n".join(lines)
    except Exception:
        st.error("❌ Textract 识别失败：'DetectedText' 字段缺失，可能是上传的文件不清晰或不符合要求。")
        os.remove(tmp_path)
        st.stop()

    # 展示识别结果
    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 分析 quote 内容并生成保单
    quote_data = parse_quote_from_text(extracted_text)
    output_path = generate_policy_doc(quote_data)

    # 下载按钮
    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # 清理临时文件
    os.remove(tmp_path)
