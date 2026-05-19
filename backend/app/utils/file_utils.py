import uuid
from pathlib import Path
from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def validate_file(filename: str, file_size: int) -> str | None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"不支持的文件格式 {ext}，仅支持 .pdf 和 .docx"
    if file_size > MAX_FILE_SIZE:
        return f"文件大小超过限制（最大50MB）"
    return None


def save_upload(content: bytes, original_filename: str) -> tuple[str, str]:
    ext = Path(original_filename).suffix.lower()
    file_type = ext.lstrip(".")
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = Path(settings.upload_dir) / unique_name
    file_path.write_bytes(content)
    return str(file_path), file_type
