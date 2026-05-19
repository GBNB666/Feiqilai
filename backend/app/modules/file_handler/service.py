"""文件验证、存储、下载服务"""
import uuid
from pathlib import Path
from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class FileService:
    @staticmethod
    def validate(filename: str, file_size: int) -> str | None:
        """验证文件，返回错误信息或None"""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return f"不支持的文件格式: {ext}，仅支持 .docx / .pdf"
        if file_size > MAX_FILE_SIZE:
            return f"文件过大: {file_size / 1024 / 1024:.1f}MB，上限50MB"
        if file_size == 0:
            return "文件为空"
        return None

    @staticmethod
    def save(file_bytes: bytes, original_name: str) -> tuple[str, str]:
        """保存上传文件，返回 (文件路径, 文件类型)"""
        ext = Path(original_name).suffix.lower()
        file_type = ext.lstrip(".")  # "docx" or "pdf"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = str(Path(settings.upload_dir) / unique_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path, file_type

    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """提取文档纯文本（供AI分析用），截断到20000字符"""
        if file_type == "docx":
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
        elif file_type == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages)
        else:
            return ""

        if len(text) > 20000:
            cut = text.rfind("\n", 19000, 20000)
            if cut == -1:
                cut = 20000
            text = text[:cut]
        return text

    @staticmethod
    def get_output_path(job_id: str) -> Path | None:
        """获取下载文件路径"""
        candidate = Path(settings.output_dir) / f"{job_id}.docx"
        if candidate.exists():
            return candidate
        return None
