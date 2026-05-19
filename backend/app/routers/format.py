from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import FormatJob, JobStatus
from app.schemas.job import (
    JobResponse, ModeSelectRequest, AnnotationRequest,
    CustomizeRequest, ModifySectionRequest,
    FormatSettings, FormatSettingsEnabled,
)
from app.services.formatter import run_formatting
from app.services.ai_analyzer import analyze_paper_structure, detect_format_warnings

router = APIRouter()


@router.post("/format/select-mode", response_model=JobResponse)
def select_mode(req: ModeSelectRequest, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    job.format_mode = req.format_mode
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.post("/format/analyze", response_model=JobResponse)
def start_analysis(job_id: str, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    job.status = JobStatus.ANALYZING.value
    db.commit()
    try:
        structure = analyze_paper_structure(job.file_path, job.file_type)
        warnings = detect_format_warnings(structure)
        job.ai_analysis = str({"structure": structure, "warnings": warnings})
        job.status = JobStatus.ANALYZED.value
    except Exception as e:
        job.status = JobStatus.FAILED.value
        db.commit()
        raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.post("/format/annotate", response_model=JobResponse)
def submit_annotations(req: AnnotationRequest, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    if job.format_mode != "manual":
        raise HTTPException(status_code=400, detail="当前模式不支持手动标注")
    job.user_annotations = req.annotations
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.post("/format/customize", response_model=JobResponse)
def customize_settings(req: CustomizeRequest, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    import json
    payload = {"settings": req.settings.model_dump(), "enabled": req.enabled.model_dump() if req.enabled else {}}
    job.user_annotations = json.dumps(payload, ensure_ascii=False)
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.post("/format/execute", response_model=JobResponse)
def execute_formatting(job_id: str, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    if job.status not in [JobStatus.ANALYZED.value, JobStatus.UPLOADED.value]:
        raise HTTPException(status_code=400, detail="请先完成AI分析")
    job.status = JobStatus.FORMATTING.value
    db.commit()
    try:
        custom_settings = None
        custom_enabled = None
        if job.user_annotations:
            import json
            try:
                data = json.loads(job.user_annotations)
                if "settings" in data:
                    custom_settings = FormatSettings.model_validate(data["settings"])
                    if "enabled" in data and data["enabled"]:
                        custom_enabled = FormatSettingsEnabled.model_validate(data["enabled"])
                elif "font_name" not in data and "page_margin_top" in data:
                    custom_settings = FormatSettings.model_validate(data)
            except Exception:
                pass
        run_formatting(job, custom_settings, custom_enabled)
    except Exception as e:
        job.status = JobStatus.FAILED.value
        db.commit()
        raise HTTPException(status_code=500, detail=f"排版失败: {str(e)}")
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.post("/format/modify-section/{job_id}", response_model=JobResponse)
def modify_section(job_id: str, req: ModifySectionRequest, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    if not job.output_path:
        raise HTTPException(status_code=400, detail="请先完成排版")
    from app.services.docx_processor import modify_section_content
    modify_section_content(job.output_path, req.section_index, req.new_content)
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.get("/format/job/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return JobResponse.model_validate(job)
