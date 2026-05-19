"""FormatTemplate 数据模型"""
from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class FormatTemplate(Base):
    __tablename__ = "format_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    settings_json = Column(String(50000), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
