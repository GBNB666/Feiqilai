"""排版引擎 API 路由"""
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.modules.job_manager.models import JobStatus
from app.modules.job_manager.service import JobService
from app.modules.format_engine.service import FormatEngine

router = APIRouter()


class AnnotationRequest(BaseModel):
    job_id: str
    annotations: str


class CustomizeRequest(BaseModel):
    job_id: str
    settings: dict | None = None
    enabled: dict | None = None


class ModifySectionRequest(BaseModel):
    section_index: int
    new_content: str


@router.post("/api/format/annotate")
async def submit_annotations(req: AnnotationRequest, db: Session = Depends(get_db)):
    """保存手动标注"""
    job = JobService.get_or_404(req.job_id, db)
    JobService.save_annotations(req.job_id, req.annotations, db)
    return {"job_id": req.job_id, "status": "annotated"}


@router.post("/api/format/customize")
async def customize_settings(req: CustomizeRequest, db: Session = Depends(get_db)):
    """保存自定义格式设置"""
    job = JobService.get_or_404(req.job_id, db)
    data = {"settings": req.settings, "enabled": req.enabled}
    job.user_annotations = json.dumps(data, ensure_ascii=False)
    db.commit()
    return {"job_id": req.job_id, "status": "customized"}


@router.post("/api/format/execute")
async def execute_formatting(
    job_id: str = Query(..., description="任务ID"),
    db: Session = Depends(get_db),
):
    """执行排版"""
    job = JobService.get_or_404(job_id, db)

    try:
        JobService.set_status(job_id, JobStatus.FORMATTING, db)

        # 解析 AI 分析结果
        if not job.ai_analysis:
            raise ValueError("未找到 AI 分析结果，请先执行分析")

        structure = json.loads(job.ai_analysis)

        # 解析自定义设置
        custom_settings = None
        enabled_flags = None
        if job.user_annotations:
            try:
                annot_data = json.loads(job.user_annotations)
                custom_settings = annot_data.get("settings")
                enabled_flags = annot_data.get("enabled")
            except (json.JSONDecodeError, AttributeError):
                pass

        # 确定输出路径（绝对路径，防止 CWD 变化导致文件找不到）
        output_path = str(
            Path(settings.output_dir).resolve() / f"{job_id}.docx"
        )

        # 执行排版
        FormatEngine.execute(
            input_path=job.file_path,
            output_path=output_path,
            structure=structure,
            custom_settings=custom_settings,
            enabled_flags=enabled_flags,
        )

        # 强制 .docx 扩展名
        actual_output = output_path
        if job.file_type == "pdf":
            actual_output = str(Path(output_path).with_suffix(".docx"))

        JobService.save_output(job_id, actual_output, db)
        JobService.set_status(job_id, JobStatus.COMPLETED, db)

        return {
            "job_id": job_id,
            "status": "completed",
            "download_url": f"/api/download/{job_id}",
        }

    except Exception as e:
        JobService.set_status(job_id, JobStatus.FAILED, db)
        raise HTTPException(status_code=500, detail=f"排版失败: {str(e)}")


@router.post("/api/format/modify-section/{job_id}")
async def modify_section(
    job_id: str,
    req: ModifySectionRequest,
    db: Session = Depends(get_db),
):
    """修改单个章节的正文内容"""
    job = JobService.get_or_404(job_id, db)
    if not job.output_path:
        raise HTTPException(status_code=400, detail="尚未排版，请先执行排版")

    # 重新排版：修改指定section内容后重新生成
    structure = json.loads(job.ai_analysis) if job.ai_analysis else {}
    sections = structure.get("sections", [])
    if req.section_index < 0 or req.section_index >= len(sections):
        raise HTTPException(status_code=400, detail="无效的章节索引")

    sections[req.section_index]["content_summary"] = req.new_content

    FormatEngine.execute(
        input_path=job.file_path,
        output_path=job.output_path,
        structure=structure,
    )

    return {"job_id": job_id, "status": "updated"}
