import streamlit as st
import boto3
import tempfile
import os

# 读取 AWS 凭证
aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
aws_region = os.environ.get("AWS_REGION", "us-east-1")

st.title("保险报价解析工具")

uploaded_file = st.file_uploader("上传保险 Quote（PDF）", type=["pdf"])

if uploaded_file is not None:
    st.success(f"上传成功！文件名：{uploaded_file.name}")

    # 创建 Textract 客户端
    textract = boto3.client(
        "textract",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    # 保存上传的 PDF 文件到临时路径
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # 使用 Textract 分析文档内容（支持多页 PDF）
    with open(tmp_path, "rb") as doc:
        response = textract.analyze_document(
            Document={"Bytes": doc.read()},
            FeatureTypes=["FORMS"]
        )

    # 提取文字块并展示
    text_blocks = []
    for block in response["Blocks"]:
        if block["BlockType"] == "LINE":
            text_blocks.append(block["Text"])

    st.subheader("识别出的文字内容：")
    st.text("\n".join(text_blocks[:50]))  # 只展示前50行，避免太长

    # 可扩展：将 text_blocks 转为结构化数据、填入模板等
