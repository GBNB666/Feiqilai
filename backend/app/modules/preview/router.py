import json, os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.job_manager.service import JobService
from app.modules.preview.service import PreviewService
from app.shared.schemas import PreviewResponse, FormatWarnings, ContentMarker
from app.modules.ai_analyzer.warnings import detect_warnings

router = APIRouter(prefix="/api/preview", tags=["preview"])


@router.get("/{job_id}")
def get_preview(job_id: str, db: Session = Depends(get_db)):
    job = JobService.get(job_id, db)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    if not job.ai_analysis:
        raise HTTPException(status_code=400, detail="请先完成AI分析")

    try:
        structure = json.loads(job.ai_analysis)
        # 优先读取排版后的输出文件
        src_path = getattr(job, "output_path", None) or job.file_path
        if not src_path or not os.path.exists(src_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {src_path}")
        sections = PreviewService.extract(src_path, structure)
        warnings = detect_warnings(structure)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")

    return PreviewResponse(
        job_id=job.id,
        title=structure.get("title", ""),
        sections=[
            {
                "level": s["level"],
                "title": s["title"],
                "content": s["content"],
                "markers": [ContentMarker(**m) for m in s["markers"]],
                "is_toc": s["is_toc"],
                "font_info": s.get("font_info"),
                "body_sample": s.get("body_sample"),
            }
            for s in sections
        ],
        warnings=warnings,
    )
