import streamlit as st

st.set_page_config(page_title="保单生成系统", layout="centered")

st.title("保单生成系统")
st.write("欢迎使用保单自动生成工具。请上传报价 PDF 文件。")

uploaded_file = st.file_uploader("📄 上传报价 PDF 文件", type=["pdf"])

if uploaded_file is not None:
    st.success("上传成功！文件名：" + uploaded_file.name)
    # 后续可以在这里加 OCR 和生成保单的逻辑
