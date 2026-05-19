"""AI 分析 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.job_manager.models import JobStatus
from app.modules.job_manager.service import JobService
from app.modules.ai_analyzer.service import AIService

router = APIRouter()


@router.post("/api/format/analyze")
async def start_analysis(
    job_id: str = Query(..., description="任务ID"),
    db: Session = Depends(get_db),
):
    """启动 AI 论文结构分析"""
    job = JobService.get_or_404(job_id, db)

    try:
        JobService.set_status(job_id, JobStatus.ANALYZING, db)
        structure = AIService.analyze(job.file_path, job.file_type)
        warnings = AIService.detect_warnings(structure)
        structure["_warnings"] = warnings

        JobService.save_analysis(job_id, structure, db)
        JobService.set_status(job_id, JobStatus.ANALYZED, db)

        return {
            "id": job_id,
            "status": "analyzed",
            "structure": structure,
            "warnings": warnings,
        }

    except Exception as e:
        JobService.set_status(job_id, JobStatus.FAILED, db)
        raise HTTPException(status_code=502, detail=f"AI 分析失败: {str(e)}")
