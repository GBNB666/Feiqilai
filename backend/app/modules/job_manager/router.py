from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.job_manager.service import JobService
from app.shared.schemas import SelectModeRequest, JobResponse, ErrorResponse
from app.shared.errors import NotFoundError, ConflictError

router = APIRouter(prefix="/api/format", tags=["format"])


@router.post(
    "/select-mode",
    response_model=JobResponse,
    responses={404: {"model": ErrorResponse}},
)
def select_mode(body: SelectModeRequest, db: Session = Depends(get_db)):
    job = JobService.get(body.job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {body.job_id}")
    # 状态机守卫：仅 UPLOADED 或 FAILED 状态可进入分析
    if job.status not in ("UPLOADED", "FAILED"):
        raise ConflictError(f"当前状态 {job.status} 不允许选择模式，请重新上传文件")
    job.format_mode = body.format_mode.value
    db.commit()
    db.refresh(job)
    return JobService.to_response(job)


@router.get(
    "/job/{job_id}",
    response_model=JobResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = JobService.get(job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {job_id}")
    return JobService.to_response(job)
