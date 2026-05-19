"""文件处理 API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.file_handler.service import FileService
from app.modules.job_manager.service import JobService

router = APIRouter()


@router.post("/api/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传论文文件"""
    content = await file.read()
    filename = file.filename or "unknown"

    error = FileService.validate(filename, len(content))
    if error:
        raise HTTPException(status_code=400, detail=error)

    file_path, file_type = FileService.save(content, filename)
    job = JobService.create(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        db=db,
    )

    return JobService.to_response(job)


@router.get("/api/download/{job_id}")
async def download_result(job_id: str, db: Session = Depends(get_db)):
    """下载排版结果文件"""
    job = JobService.get_or_404(job_id, db)

    output_path = FileService.get_output_path(job_id)
    if output_path is None:
        raise HTTPException(status_code=404, detail="排版结果文件不存在，请先执行排版")

    return FileResponse(
        path=str(output_path),
        filename=f"formatted_{job.original_filename}",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
