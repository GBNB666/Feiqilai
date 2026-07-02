import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.modules.job_manager.models import FormatJob
from app.shared.schemas import JobResponse, StructureOutput, FormatWarnings


class JobService:
    @staticmethod
    def create(
        filename: str,
        file_path: str,
        file_type: str,
        db: Session,
    ) -> FormatJob:
        job = FormatJob(
            original_filename=filename,
            file_path=file_path,
            file_type=file_type,
            status="UPLOADED",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get(job_id: str, db: Session) -> FormatJob | None:
        return db.query(FormatJob).filter(FormatJob.id == job_id).first()

    @staticmethod
    def set_status(job_id: str, status: str, db: Session) -> FormatJob:
        job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
        if job is None:
            raise ValueError(f"Job not found: {job_id}")
        job.status = status
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save_analysis(job_id: str, analysis_dict: dict, db: Session) -> FormatJob:
        job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
        if job is None:
            raise ValueError(f"Job not found: {job_id}")
        job.ai_analysis = json.dumps(analysis_dict, ensure_ascii=False)
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save_annotations(job_id: str, annotations_json: str, db: Session) -> FormatJob:
        job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
        if job is None:
            raise ValueError(f"Job not found: {job_id}")
        job.user_annotations = annotations_json
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save_output(job_id: str, output_path: str, db: Session) -> FormatJob:
        job = db.query(FormatJob).filter(FormatJob.id == job_id).first()
        if job is None:
            raise ValueError(f"Job not found: {job_id}")
        job.output_path = output_path
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def to_response(job: FormatJob) -> JobResponse:
        import os
        analysis = None
        if job.ai_analysis:
            try:
                raw = json.loads(job.ai_analysis)
                analysis = StructureOutput(**raw)
            except (json.JSONDecodeError, Exception):
                pass

        char_count = 0
        estimated_pages = 0
        try:
            if job.file_path and os.path.exists(job.file_path):
                from app.modules.format_engine.text_stats import count_text, estimate_pages
                stats = count_text(job.file_path)
                char_count = stats["char_count"]
                # Estimate pages with default academic settings
                estimated_pages = estimate_pages(char_count)
        except Exception:
            pass

        return JobResponse(
            id=job.id,
            original_filename=job.original_filename,
            file_type=job.file_type,
            format_mode=job.format_mode,
            status=job.status,
            price=job.price or 9.9,
            created_at=job.created_at,
            updated_at=job.updated_at,
            analysis=analysis,
            warnings=None,
            char_count=char_count,
            estimated_pages=estimated_pages,
        )
