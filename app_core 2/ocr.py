def extract_text_from_pdf(file_path):
    # 模拟从 PDF 中提取文本内容
    with open(file_path, 'rb') as f:
        return f.read().decode(errors='ignore')
