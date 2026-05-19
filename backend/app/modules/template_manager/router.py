"""模板管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.template_manager.service import TemplateService

router = APIRouter()


class TemplateSaveRequest(BaseModel):
    name: str
    settings: dict


@router.post("/api/templates/save")
async def save_template(req: TemplateSaveRequest, db: Session = Depends(get_db)):
    """保存模板（创建或更新）"""
    import json
    template = TemplateService.create_or_update(
        req.name,
        json.dumps(req.settings, ensure_ascii=False),
        db,
    )
    return {
        "id": template.id,
        "name": template.name,
        "settings": req.settings,
        "created_at": template.created_at.isoformat() if template.created_at else None,
    }


@router.get("/api/templates/")
async def list_templates(db: Session = Depends(get_db)):
    templates = TemplateService.list_all(db)
    import json
    return [
        {
            "id": t.id,
            "name": t.name,
            "settings": json.loads(t.settings_json) if t.settings_json else {},
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in templates
    ]


@router.get("/api/templates/{template_id}")
async def get_template(template_id: int, db: Session = Depends(get_db)):
    template = TemplateService.get(template_id, db)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    import json
    return {
        "id": template.id,
        "name": template.name,
        "settings": json.loads(template.settings_json) if template.settings_json else {},
        "created_at": template.created_at.isoformat() if template.created_at else None,
    }


@router.delete("/api/templates/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    deleted = TemplateService.delete(template_id, db)
    if not deleted:
        raise HTTPException(status_code=400, detail="无法删除该模板")
    return {"status": "deleted"}
