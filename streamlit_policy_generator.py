import streamlit as st
import boto3
import tempfile
import os
from utils.parse_quote import parse_quote_from_text
from utils.generate_policy import generate_policy_doc

# 页面设置
st.set_page_config(page_title="中文保单生成系统", layout="wide")
st.title("📄 中文保单生成系统")

uploaded_file = st.file_uploader("上传保险 Quote 文件（支持 PDF / PNG / JPG）", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ 上传成功：{uploaded_file.name}")

    # 创建 AWS Textract 客户端（使用 secrets 管理凭证）
    textract = boto3.client(
        "textract",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )

    # 判断文件类型
    suffix = os.path.splitext(uploaded_file.name)[-1].lower()
    is_pdf = suffix == ".pdf"
    is_image = suffix in [".png", ".jpg", ".jpeg"]

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    with open(tmp_path, "rb") as doc:
        try:
            if is_pdf:
                response = textract.analyze_document(
                    Document={"Bytes": doc.read()},
                    FeatureTypes=["TABLES", "FORMS"]
                )
            elif is_image:
                response = textract.detect_document_text(Document={"Bytes": doc.read()})
            else:
                st.error("❌ 文件格式不被支持，请上传 PDF 或图片（PNG/JPG）。")
                st.stop()
        except Exception as e:
            st.error(f"❌ Textract 识别失败：{str(e)}")
            st.stop()

    # 提取识别文本
    try:
        extracted_text = "\n".join(
            [item["DetectedText"] for item in response["Blocks"] if item["BlockType"] == "LINE"]
        )
    except Exception:
        st.error("❌ Textract 返回格式错误或无法识别文本。请检查文件是否清晰。")
        st.stop()

    with st.expander("📃 查看识别文本"):
        st.text(extracted_text)

    # 结构化解析 quote 内容
    quote_data = parse_quote_from_text(extracted_text)

    # 生成保单 Word 文件
    template_path = "保单范例.docx"
    output_path = "output_policy.docx"
    generate_policy_doc(template_path, output_path, quote_data)

    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 下载中文保单",
            data=f,
            file_name="保单说明.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # 清理临时文件
    os.remove(tmp_path)
