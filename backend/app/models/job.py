import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
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

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    format_mode: Mapped[str] = mapped_column(String(10), nullable=False, default=FormatMode.AUTO.value)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=JobStatus.UPLOADED.value)
    ai_analysis: Mapped[str | None] = mapped_column(String(10000), nullable=True)
    user_annotations: Mapped[str | None] = mapped_column(String(10000), nullable=True)
    output_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=9.9)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
