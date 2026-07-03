"""学校模板 — 提供各高校论文格式要求模板，支持用户自定义保存。"""

from __future__ import annotations
import json
import os
from pathlib import Path
from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.shared.schemas import (
    FormatSettingsModel,
    PageSettingsModel,
    FormatItemModel,
    FooterPageNumberModel,
)

router = APIRouter(prefix="/api/school-templates", tags=["school-templates"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "school_templates"


def _user_templates_dir() -> Path:
    """用户自定义模板保存到数据目录（开发: backend/data/my_templates/，exe: %APPDATA%/AI智排/my_templates/）。"""
    from app.config import get_settings
    settings = get_settings()
    p = Path(settings.data_dir) / "my_templates"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_all() -> list[dict]:
    items: list[dict] = []
    # 加载内置模板
    if DATA_DIR.is_dir():
        for f in sorted(DATA_DIR.glob("*.json")):
            try:
                items.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
    # 加载用户自定义模板
    user_dir = _user_templates_dir()
    for f in sorted(user_dir.glob("*.json")):
        try:
            items.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return items


def _load_one(tid: str) -> dict | None:
    path = DATA_DIR / f"{tid}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    path = _user_templates_dir() / f"{tid}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


class SaveTemplateBody(BaseModel):
    name: str
    description: str = ""
    source: str = "用户自定义"
    format_settings: dict


# ── List ──────────────────────────────────────────────────


@router.get("/")
def list_templates():
    """返回所有学校模板的摘要列表（含内置 + 用户自定义）。"""
    all_items = _load_all()
    summaries = []
    for t in all_items:
        summaries.append({
            "id": t["id"],
            "name": t["name"],
            "description": t.get("description", ""),
            "source": t.get("source", ""),
            "rule_count": len(t.get("special_rules", [])),
        })
    return {"templates": summaries, "count": len(summaries)}


# ── Save ──────────────────────────────────────────────────


@router.post("/")
def save_template(body: SaveTemplateBody):
    """保存当前格式设置为新的学校模板。"""
    import re, hashlib
    # 提取名字中的字母数字；全非拉丁字符（如中文）则用 MD5 hash
    safe = re.sub(r"[^a-z0-9]", "-", body.name.strip().lower())
    safe = re.sub(r"-{2,}", "-", safe).strip("-")
    if not any(c.isalnum() for c in safe) or len(safe) < 3:
        tid = hashlib.md5(body.name.encode()).hexdigest()[:8]
    else:
        tid = safe[:50]

    # Check uniqueness
    base_tid = tid
    counter = 1
    while _load_one(tid) is not None:
        tid = f"{base_tid}-{counter}"
        counter += 1

    template = {
        "id": tid,
        "name": body.name,
        "description": body.description,
        "source": body.source,
        "format_settings": body.format_settings,
        "special_rules": [],
        "extra_notes": {},
    }
    path = _user_templates_dir() / f"{tid}.json"
    path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": tid, "name": body.name, "message": "模板已保存"}


# ── Detail ────────────────────────────────────────────────


@router.get("/{template_id}")
def get_template(template_id: str):
    """返回某个学校模板的完整详情（含格式设置和特殊规则）。"""
    t = _load_one(template_id)
    if t is None:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "模板不存在"}, status_code=404)
    return t


# ── Format settings as apply-able payload ─────────────────


@router.get("/{template_id}/settings")
def get_template_settings(template_id: str) -> FormatSettingsModel:
    """返回模板对应的 FormatSettingsModel，可直接用于 customize。"""
    t = _load_one(template_id)
    if t is None:
        from fastapi import HTTPException
        raise HTTPException(404, "模板不存在")

    fs = t["format_settings"]

    def _item(data: dict) -> FormatItemModel:
        return FormatItemModel(**data)

    page = PageSettingsModel(**fs.get("page", {}))
    return FormatSettingsModel(
        page=page,
        title=_item(fs.get("title", {})),
        heading_1=_item(fs.get("heading_1", {})),
        heading_2=_item(fs.get("heading_2", {})),
        heading_3=_item(fs.get("heading_3", {})),
        body=_item(fs.get("body", {})),
        table_caption=_item(fs.get("table_caption", {})),
        figure_caption=_item(fs.get("figure_caption", {})),
        reference=_item(fs.get("reference", {})),
        toc_enabled=fs.get("toc_enabled", True),
        header_footer=_item(fs.get("header_footer", {})),
        toc_title=_item(fs.get("toc_title", {})),
        toc_entry=_item(fs.get("toc_entry", {})),
        table_text=_item(fs.get("table_text", {})),
        footer_page_number=FooterPageNumberModel(**fs.get("footer_page_number", {})),
        latin_font=fs.get("latin_font", True),
        template=fs.get("template", template_id),
    )
