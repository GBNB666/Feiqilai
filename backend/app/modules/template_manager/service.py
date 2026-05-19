"""模板管理服务"""
from sqlalchemy.orm import Session
from app.modules.template_manager.models import FormatTemplate

DEFAULT_TEMPLATE = "系统默认"


class TemplateService:
    @staticmethod
    def create_or_update(name: str, settings_json: str, db: Session) -> FormatTemplate:
        existing = db.query(FormatTemplate).filter(FormatTemplate.name == name).first()
        if existing:
            existing.settings_json = settings_json
            db.commit()
            db.refresh(existing)
            return existing
        template = FormatTemplate(name=name, settings_json=settings_json)
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def list_all(db: Session) -> list[FormatTemplate]:
        return db.query(FormatTemplate).order_by(FormatTemplate.created_at.desc()).all()

    @staticmethod
    def get(template_id: int, db: Session) -> FormatTemplate | None:
        return db.query(FormatTemplate).filter(FormatTemplate.id == template_id).first()

    @staticmethod
    def delete(template_id: int, db: Session) -> bool:
        template = TemplateService.get(template_id, db)
        if template is None:
            return False
        if template.name == DEFAULT_TEMPLATE:
            return False
        db.delete(template)
        db.commit()
        return True

    @staticmethod
    def seed_default(db: Session) -> None:
        existing = db.query(FormatTemplate).filter(FormatTemplate.name == DEFAULT_TEMPLATE).first()
        if not existing:
            import json
            from app.modules.format_standards.custom import merge_settings
            defaults = merge_settings(None, None)
            TemplateService.create_or_update(
                DEFAULT_TEMPLATE,
                json.dumps(defaults, ensure_ascii=False),
                db,
            )
