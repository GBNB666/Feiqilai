import json
from sqlalchemy.orm import Session
from app.modules.template_manager.models import FormatTemplate

DEFAULT_SETTINGS = {
    "page": {"enabled": False, "paper_size": "A4", "orientation": "portrait",
             "margin_top": 2.54, "margin_bottom": 2.54, "margin_left": 3.17, "margin_right": 3.17,
             "header_distance": 1.5, "footer_distance": 1.75},
    "title": {"font_name": "黑体", "font_size_pt": 22, "bold": True, "alignment": "CENTER"},
    "heading_1": {"font_name": "黑体", "font_size_pt": 16, "bold": True, "alignment": "CENTER"},
    "heading_2": {"font_name": "黑体", "font_size_pt": 14, "bold": True, "alignment": "LEFT"},
    "heading_3": {"font_name": "黑体", "font_size_pt": 12, "bold": True, "alignment": "LEFT"},
    "body": {"font_name": "宋体", "font_size_pt": 12, "alignment": "JUSTIFY", "line_spacing": 1.5,
             "first_line_indent": 0.74},
    "table_caption": {"font_name": "宋体", "font_size_pt": 10.5, "alignment": "CENTER"},
    "figure_caption": {"font_name": "宋体", "font_size_pt": 10.5, "alignment": "CENTER"},
    "reference": {"font_name": "宋体", "font_size_pt": 10.5, "alignment": "LEFT",
                  "line_spacing": 1.0, "hanging_indent": 0.74},
    "header_footer": {"font_name": "宋体", "font_size_pt": 9, "alignment": "CENTER"},
    "toc_title": {"font_name": "黑体", "font_size_pt": 16, "bold": True, "alignment": "CENTER"},
    "toc_entry": {"font_name": "宋体", "font_size_pt": 12, "alignment": "LEFT", "line_spacing": 1.5},
    "table_text": {"font_name": "宋体", "font_size_pt": 10.5},
    "latin_font": True,
    "toc_enabled": False,
    "template": "academic",
}

DEFAULT_TEMPLATE = {
    "name": "系统默认 (学术论文)",
    "settings_json": json.dumps(DEFAULT_SETTINGS, ensure_ascii=False),
}


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
        template = db.query(FormatTemplate).filter(FormatTemplate.id == template_id).first()
        if template is None:
            return False
        if template.name == "系统默认":
            return False
        db.delete(template)
        db.commit()
        return True

    @staticmethod
    def seed_default(db: Session) -> None:
        existing = db.query(FormatTemplate).filter(FormatTemplate.name == "系统默认").first()
        if existing is None:
            template = FormatTemplate(
                name=DEFAULT_TEMPLATE["name"],
                settings_json=DEFAULT_TEMPLATE["settings_json"],
            )
            db.add(template)
            db.commit()
