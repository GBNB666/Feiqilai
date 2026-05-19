from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.config import settings
from app.models.job import FormatJob, JobStatus

router = APIRouter()

OUTPUT_DIR = Path(settings.output_dir).resolve()


def _resolve_path(job: FormatJob) -> Path:
    """将存储的输出路径解析为绝对路径"""
    if not job.output_path:
        raise HTTPException(status_code=404, detail="输出文件不存在")
    p = Path(job.output_path)
    if p.is_absolute():
        return p
    return OUTPUT_DIR / p.name


@router.get("/download/{job_id}")
def download_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="排版尚未完成")

    file_path = _resolve_path(job)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="输出文件不存在")

    download_name = f"formatted_{job.original_filename}"
    return FileResponse(
        path=str(file_path),
        filename=download_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
