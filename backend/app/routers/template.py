import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.template import FormatTemplate
from app.schemas.job import TemplateSaveRequest, TemplateResponse, FormatSettings

router = APIRouter()


@router.post("/templates/save", response_model=TemplateResponse)
def save_template(req: TemplateSaveRequest, db: Session = Depends(get_db)):
    existing = db.query(FormatTemplate).filter(FormatTemplate.name == req.name).first()
    if existing:
        existing.settings_json = req.settings.model_dump_json()
        db.commit()
        db.refresh(existing)
        return TemplateResponse(
            id=existing.id,
            name=existing.name,
            settings=req.settings,
            created_at=existing.created_at.isoformat(),
        )
    tmpl = FormatTemplate(name=req.name, settings_json=req.settings.model_dump_json())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return TemplateResponse(
        id=tmpl.id, name=tmpl.name, settings=req.settings,
        created_at=tmpl.created_at.isoformat(),
    )


@router.get("/templates/", response_model=list[TemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(FormatTemplate).order_by(FormatTemplate.created_at.desc()).all()
    return [
        TemplateResponse(
            id=t.id, name=t.name,
            settings=FormatSettings.model_validate_json(t.settings_json),
            created_at=t.created_at.isoformat(),
        )
        for t in templates
    ]


@router.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    t = db.query(FormatTemplate).filter(FormatTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    return TemplateResponse(
        id=t.id, name=t.name,
        settings=FormatSettings.model_validate_json(t.settings_json),
        created_at=t.created_at.isoformat(),
    )


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    t = db.query(FormatTemplate).filter(FormatTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    if t.name == "系统默认":
        raise HTTPException(status_code=400, detail="系统默认模板不可删除")
    db.delete(t)
    db.commit()
    return {"status": "ok"}
