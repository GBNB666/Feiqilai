"""预览 API 路由"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.job_manager.service import JobService
from app.modules.preview.service import PreviewService

router = APIRouter()


@router.get("/api/preview/{job_id}")
async def get_preview(job_id: str, db: Session = Depends(get_db)):
    """获取排版结果预览"""
    job = JobService.get_or_404(job_id, db)

    if not job.ai_analysis:
        raise HTTPException(status_code=400, detail="未找到分析结果")

    structure = json.loads(job.ai_analysis)
    file_path = job.output_path or job.file_path

    sections = PreviewService.extract(file_path, structure)

    return {
        "job_id": job_id,
        "title": structure.get("title", ""),
        "section_count": len(sections),
        "sections": sections,
    }
