from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime
from app.database import Base
import uuid


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FormatJob(Base):
    __tablename__ = "format_jobs"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(4), nullable=False)
    format_mode = Column(String(10), nullable=True)
    status = Column(String(20), nullable=False, default="UPLOADED")
    ai_analysis = Column(String(50000), nullable=True)
    user_annotations = Column(String(50000), nullable=True)
    output_path = Column(String(500), nullable=True)
    price = Column(Float, default=9.9)
    created_at = Column(DateTime, nullable=False, default=_utc_now)
    updated_at = Column(DateTime, nullable=True, onupdate=_utc_now)
