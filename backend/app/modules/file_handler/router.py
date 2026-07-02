import os
from fastapi import APIRouter, UploadFile, File, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.file_handler.service import FileService
from app.modules.job_manager.service import JobService
from app.shared.schemas import JobResponse
from app.shared.errors import FileValidationError, NotFoundError, FormatError

router = APIRouter(prefix="/api", tags=["files"])

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=JobResponse, status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db), request: Request = None):
    # 先检查 Content-Length（如果可用），避免大文件先读入内存
    if request:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_SIZE:
            raise FileValidationError(f"文件过大（>{MAX_UPLOAD_SIZE // 1024 // 1024}MB），请压缩后重试")

    content = await file.read()
    # 二次检查实际大小（防止 Content-Length 被伪造跳过）
    if len(content) > MAX_UPLOAD_SIZE:
        raise FileValidationError(f"文件过大（>{MAX_UPLOAD_SIZE // 1024 // 1024}MB），请压缩后重试")

    error = FileService.validate(file.filename, len(content))
    if error:
        raise FileValidationError(error)

    file_type = os.path.splitext(file.filename)[1].lower().lstrip(".")
    job_id, saved_path = FileService.save(content, file.filename)
    job = JobService.create(
        filename=file.filename,
        file_path=saved_path,
        file_type=file_type,
        db=db,
    )
    job.id = job_id
    db.commit()
    db.refresh(job)
    return JobService.to_response(job)


@router.get("/download/{job_id}")
def download(job_id: str, fmt: str = Query("docx", alias="format"), db: Session = Depends(get_db)):
    job = JobService.get(job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {job_id}")

    if fmt not in ("docx", "pdf"):
        raise FileValidationError(f"不支持的格式: {fmt}，仅支持 docx / pdf")

    if fmt == "pdf":
        try:
            output_path = FileService.convert_to_pdf(job_id)
        except RuntimeError as e:
            raise FormatError(str(e))
    else:
        output_path = FileService.get_output_path(job_id, "docx")

    if output_path is None:
        raise NotFoundError("输出文件不存在，请先执行排版")

    base_name = os.path.splitext(job.original_filename)[0]
    ext = ".pdf" if fmt == "pdf" else ".docx"
    download_name = f"{base_name}_排版完成{ext}"

    media = ("application/pdf" if fmt == "pdf"
             else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    return FileResponse(path=str(output_path), filename=download_name, media_type=media)
