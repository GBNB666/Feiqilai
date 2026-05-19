"""任务管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.modules.job_manager.service import JobService

router = APIRouter()


class ModeSelectRequest(BaseModel):
    job_id: str
    format_mode: str  # "auto" or "manual"


@router.post("/api/format/select-mode")
async def select_mode(req: ModeSelectRequest, db: Session = Depends(get_db)):
    """选择排版模式"""
    if req.format_mode not in ("auto", "manual"):
        raise HTTPException(status_code=400, detail="模式必须为 auto 或 manual")
    job = JobService.get_or_404(req.job_id, db)
    job.format_mode = req.format_mode
    db.commit()
    db.refresh(job)
    return JobService.to_response(job)


@router.get("/api/format/job/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """查询任务状态"""
    job = JobService.get_or_404(job_id, db)
    return JobService.to_response(job)
