"""图片格式化 API 路由。"""
import os
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database import get_db
from app.modules.job_manager.service import JobService
from app.modules.file_handler.service import FileService
from app.modules.image_formatter.engine import auto_format_images, extract_images
from app.shared.schemas import ImageExtractResponse, ExtractedImage

router = APIRouter(prefix="/api", tags=["image-formatter"])


class FormatImagesBody(BaseModel):
    width_ratio: float = Field(default=0.7, ge=0.1, le=1.0)
    image_ratios: Optional[Dict[int, float]] = None
    alignment: Optional[str] = Field(default=None, description="图片对齐: LEFT, CENTER, RIGHT 或 None 保持默认居中")


@router.get("/format-images/{job_id}/extract", response_model=ImageExtractResponse)
def extract(job_id: str, db: Session = Depends(get_db)):
    job = JobService.get(job_id, db)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    docx_path = FileService.get_output_path(job_id, "docx")
    if docx_path is None:
        raise HTTPException(status_code=404, detail="排版文件不存在，请先执行排版")

    try:
        image_list, page_width = extract_images(str(docx_path))
        return ImageExtractResponse(
            job_id=job_id,
            page_width_usable_emu=page_width,
            width_ratio_default=0.7,
            images=[ExtractedImage(**img) for img in image_list],
            count=len(image_list),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片提取失败: {str(e)}")


@router.post("/format-images/{job_id}")
def format_images(
    job_id: str,
    body: FormatImagesBody = Body(default=FormatImagesBody()),
    db: Session = Depends(get_db),
):
    job = JobService.get(job_id, db)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    docx_path = FileService.get_output_path(job_id, "docx")
    if docx_path is None:
        raise HTTPException(status_code=404, detail="排版文件不存在，请先执行排版")

    try:
        output_path, count = auto_format_images(
            str(docx_path),
            output_path=str(docx_path),  # 原地覆盖
            width_ratio=body.width_ratio,
            image_ratios=body.image_ratios,
            number_format="图{num}",
            label_position="below",
            alignment=body.alignment,
        )
        return {
            "job_id": job_id,
            "image_count": count,
            "message": f"已更新 {count} 张图片的尺寸" if count > 0 else "文档中没有检测到图片",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片格式化失败: {str(e)}")
