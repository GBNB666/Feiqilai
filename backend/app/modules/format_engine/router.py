import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.modules.job_manager.service import JobService
from app.modules.format_engine.service import FormatEngine
from app.shared.schemas import (
    JobResponse,
    CustomizePayload,
    AnnotationsPayload,
    ModifySectionPayload,
)
from app.shared.errors import NotFoundError, FormatError

router = APIRouter(prefix="/api/format", tags=["format"])


@router.post("/execute")
def execute_format(job_id: str, db: Session = Depends(get_db)):
    job = JobService.get(job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {job_id}")
    if not job.ai_analysis:
        raise NotFoundError("请先完成AI分析")

    import json
    structure = json.loads(job.ai_analysis)

    custom_settings = None
    # AUTO模式也允许用户应用自定义设置（如 toc_enabled、格式覆盖等）
    if job.user_annotations:
        try:
            annotations = json.loads(job.user_annotations)
            if isinstance(annotations, dict) and (
                "title" in annotations
                or "page" in annotations
                or "toc_enabled" in annotations
                or "body" in annotations
            ):
                custom_settings = annotations
        except json.JSONDecodeError:
            pass

    settings = get_settings()
    ext = os.path.splitext(job.original_filename)[1].lower()
    output_path = os.path.join(settings.output_dir, f"{job.id}.docx")

    try:
        JobService.set_status(job.id, "FORMATTING", db)
        # 如果已有排版输出，以其为输入（保留图片格式化等后续编辑），否则用原始文件
        existing_output = getattr(job, "output_path", None)
        input_path = existing_output if existing_output and os.path.exists(existing_output) else job.file_path
        FormatEngine.execute(
            input_path=input_path,
            output_path=output_path,
            structure=structure,
            custom_settings=custom_settings,
        )
        JobService.save_output(job.id, output_path, db)
        JobService.set_status(job.id, "COMPLETED", db)
    except Exception as e:
        JobService.set_status(job.id, "FAILED", db)
        raise FormatError(f"排版失败: {str(e)}")

    job = JobService.get(job.id, db)
    return JobService.to_response(job)


@router.post("/customize")
def customize(body: CustomizePayload, db: Session = Depends(get_db)):
    """保存自定义格式设置（暂存到 user_annotations 中）。"""
    import json
    payload = body.settings.model_dump() if body.settings else {}

    JobService.save_annotations(body.job_id, json.dumps(payload, ensure_ascii=False), db)
    return {"status": "ok"}


@router.post("/annotate")
def annotate(body: AnnotationsPayload, db: Session = Depends(get_db)):
    """保存手动标注。"""
    import json
    job = JobService.get(body.job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {body.job_id}")

    annotations_data = [a.model_dump() for a in body.annotations]
    JobService.save_annotations(body.job_id, json.dumps(annotations_data, ensure_ascii=False), db)
    return {"status": "ok"}


@router.post("/modify-section/{section_index}")
def modify_section(
    section_index: int,
    body: ModifySectionPayload,
    db: Session = Depends(get_db),
):
    """修改单个章节内容（暂存到 user_annotations）。"""
    import json
    job = JobService.get(body.job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {body.job_id}")

    modifications = {}
    if job.user_annotations:
        try:
            modifications = json.loads(job.user_annotations)
        except json.JSONDecodeError:
            pass

    modifications[f"section_{section_index}"] = body.new_content
    JobService.save_annotations(body.job_id, json.dumps(modifications, ensure_ascii=False), db)
    return {"status": "ok"}
