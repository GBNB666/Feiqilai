"""FormatJob 数据模型"""
import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, Float, DateTime
from app.database import Base
import enum


class JobStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"


class FormatMode(str, enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"


class FormatJob(Base):
    __tablename__ = "format_jobs"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(4), nullable=False)
    format_mode = Column(String(10), default=FormatMode.AUTO.value)
    status = Column(String(20), default=JobStatus.UPLOADED.value)
    ai_analysis = Column(String(50000), nullable=True)   # JSON 字符串存储
    user_annotations = Column(String(50000), nullable=True)
    output_path = Column(String(500), nullable=True)
    price = Column(Float, default=9.9)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
