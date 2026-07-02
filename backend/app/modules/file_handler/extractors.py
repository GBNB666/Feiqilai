from docx import Document
from PyPDF2 import PdfReader

MAX_CHARS = 20000


def extract_docx_text(file_path: str) -> str:
    """从 DOCX 提取文本，逐段读取，截断到 MAX_CHARS 字符（段落边界）。"""
    doc = Document(file_path)
    paragraphs = []
    total = 0
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if total + len(text) > MAX_CHARS:
            remaining = MAX_CHARS - total
            if remaining > 0:
                paragraphs.append(text[:remaining])
            break
        paragraphs.append(text)
        total += len(text)
    return "\n".join(paragraphs)


def extract_pdf_text(file_path: str) -> str:
    """从 PDF 提取文本，逐页读取，截断到 MAX_CHARS 字符。"""
    reader = PdfReader(file_path)
    paragraphs = []
    total = 0
    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        if total + len(text) > MAX_CHARS:
            remaining = MAX_CHARS - total
            if remaining > 0:
                paragraphs.append(text[:remaining])
            break
        paragraphs.append(text)
        total += len(text)
    return "\n".join(paragraphs)


def extract_text(file_path: str, file_type: str) -> str:
    """根据文件类型提取文本。"""
    if file_type == "docx":
        return extract_docx_text(file_path)
    elif file_type == "pdf":
        return extract_pdf_text(file_path)
    raise ValueError(f"Unsupported file type: {file_type}")
