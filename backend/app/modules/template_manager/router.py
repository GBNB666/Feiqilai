from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.template_manager.service import TemplateService
from app.shared.schemas import TemplateResponse, TemplateSaveRequest

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("/save", response_model=TemplateResponse)
def save_template(body: TemplateSaveRequest, db: Session = Depends(get_db)):
    template = TemplateService.create_or_update(body.name, body.settings_json, db)
    return template


@router.get("/", response_model=list[TemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    return TemplateService.list_all(db)


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = TemplateService.get(template_id, db)
    if template is None:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    ok = TemplateService.delete(template_id, db)
    if not ok:
        raise HTTPException(status_code=400, detail="系统默认模板不能删除")
    return {"status": "ok"}
