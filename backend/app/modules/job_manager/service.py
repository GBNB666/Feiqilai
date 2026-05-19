"""Job 生命周期管理"""
import json
from sqlalchemy.orm import Session
from app.modules.job_manager.models import FormatJob, JobStatus
from app.shared.errors import NotFoundError


class JobService:
    @staticmethod
    def create(filename: str, file_path: str, file_type: str, db: Session) -> FormatJob:
        job = FormatJob(
            original_filename=filename,
            file_path=file_path,
            file_type=file_type,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get(job_id: str, db: Session) -> FormatJob | None:
        return db.query(FormatJob).filter(FormatJob.id == job_id).first()

    @staticmethod
    def get_or_404(job_id: str, db: Session) -> FormatJob:
        job = JobService.get(job_id, db)
        if job is None:
            raise NotFoundError(f"任务 {job_id} 不存在")
        return job

    @staticmethod
    def set_status(job_id: str, status: JobStatus, db: Session) -> FormatJob:
        job = JobService.get_or_404(job_id, db)
        job.status = status.value
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save_analysis(job_id: str, analysis: dict, db: Session) -> FormatJob:
        """以 JSON 字符串存储 AI 分析结果"""
        job = JobService.get_or_404(job_id, db)
        job.ai_analysis = json.dumps(analysis, ensure_ascii=False)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save_annotations(job_id: str, annotations: str, db: Session) -> FormatJob:
        job = JobService.get_or_404(job_id, db)
        job.user_annotations = annotations
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save_output(job_id: str, output_path: str, db: Session) -> FormatJob:
        job = JobService.get_or_404(job_id, db)
        job.output_path = output_path
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def to_response(job: FormatJob) -> dict:
        """将 ORM 对象转为 API 响应字典"""
        return {
            "id": job.id,
            "original_filename": job.original_filename,
            "file_type": job.file_type,
            "format_mode": job.format_mode,
            "status": job.status,
            "ai_analysis": job.ai_analysis,
            "output_path": job.output_path,
            "price": job.price,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
