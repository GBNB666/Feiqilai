import ast
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import FormatJob, JobStatus
from app.schemas.job import PreviewResponse, PreviewSection
from app.services.docx_processor import extract_formatted_content

router = APIRouter()


@router.get("/preview/{job_id}", response_model=PreviewResponse)
def get_preview(job_id: str, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="排版尚未完成")
    if not job.output_path:
        raise HTTPException(status_code=404, detail="输出文件不存在")

    raw = {}
    if job.ai_analysis:
        try:
            raw = ast.literal_eval(job.ai_analysis)
        except (ValueError, SyntaxError):
            raw = {}

    # Unwrap nested structure if stored with warnings
    if "structure" in raw:
        structure = raw["structure"]
    else:
        structure = raw

    sections = extract_formatted_content(job.output_path, structure)

    return PreviewResponse(
        title=structure.get("title", job.original_filename),
        section_count=len(sections),
        sections=[PreviewSection(**s) for s in sections],
    )
