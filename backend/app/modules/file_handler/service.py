import uuid
import os
import subprocess
import shutil
from pathlib import Path
from app.config import get_settings

ALLOWED_EXTENSIONS = {".docx"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# LibreOffice headless 路径（Windows 安装默认位置）
_LO_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
]


def _find_libreoffice() -> str | None:
    """查找 LibreOffice 可执行文件。"""
    for p in _LO_PATHS:
        if os.path.exists(p):
            return p
    # fallback: 系统 PATH 中查找
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    return None


class FileService:
    @staticmethod
    def validate(filename: str, file_size: int) -> str | None:
        """验证文件。返回错误信息字符串，合法则返回 None。"""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return f"不支持的文件类型: {ext}，仅支持 .docx"
        if file_size > MAX_FILE_SIZE:
            return f"文件过大（{file_size / 1024 / 1024:.1f}MB），最大支持 20MB"
        return None

    @staticmethod
    def save(file_bytes: bytes, original_name: str) -> tuple[str, str]:
        """保存文件到 uploads 目录。返回 (file_id, saved_path)。"""
        settings = get_settings()
        file_id = uuid.uuid4().hex
        ext = os.path.splitext(original_name)[1].lower()
        saved_name = f"{file_id}{ext}"
        saved_path = os.path.join(settings.upload_dir, saved_name)
        with open(saved_path, "wb") as f:
            f.write(file_bytes)
        return file_id, saved_path

    @staticmethod
    def get_output_path(job_id: str, fmt: str = "docx") -> Path | None:
        """获取指定格式的输出文件路径。fmt: 'docx' | 'pdf'"""
        settings = get_settings()
        output_dir = Path(settings.output_dir)
        candidate = output_dir / f"{job_id}.{fmt}"
        if candidate.exists():
            return candidate
        return None

    @staticmethod
    def convert_to_pdf(job_id: str) -> Path | None:
        """用 LibreOffice headless 将输出的 docx 转为 PDF。返回 PDF 路径。"""
        # 先找 docx 输出
        docx_path = FileService.get_output_path(job_id, "docx")
        if docx_path is None:
            return None

        pdf_path = docx_path.with_suffix(".pdf")
        if pdf_path.exists():
            return pdf_path  # 已转换过，直接返回

        lo = _find_libreoffice()
        if lo is None:
            raise RuntimeError("LibreOffice 未安装，无法转换为 PDF")

        out_dir = str(docx_path.parent)
        result = subprocess.run(
            [lo, "--headless", "--convert-to", "pdf",
             "--outdir", out_dir, str(docx_path)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"PDF 转换失败: {result.stderr}")

        if pdf_path.exists():
            return pdf_path
        raise RuntimeError("PDF 转换后未找到输出文件")
