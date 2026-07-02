from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


def _utc_now():
    return datetime.now(timezone.utc)


class FormatTemplate(Base):
    __tablename__ = "format_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    settings_json = Column(String(50000), nullable=False)
    created_at = Column(DateTime, nullable=False, default=_utc_now)
