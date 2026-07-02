from docx.shared import Pt, Cm
from app.modules.format_standards import defaults


def merge_settings(custom: dict | None = None) -> tuple[dict, dict]:
    """合并用户自定义设置和默认格式。

    返回 (merged_settings, flags)
    - merged_settings: 按 section key 合并，仅当 item.enabled=True 时覆盖 custom
    - flags: {"latin_font": bool}
    """
    merged_settings = _build_default_settings()
    flags = {
        "latin_font": True,
    }

    if custom:
        format_keys = (
            "title", "heading_1", "heading_2", "heading_3",
            "body", "table_caption", "figure_caption", "reference", "header_footer",
            "toc_title", "toc_entry", "table_text",
        )
        for key in format_keys:
            item = custom.get(key, {})
            if isinstance(item, dict) and item.get("enabled") and key in merged_settings:
                merged_settings[key] = _deep_merge(merged_settings[key], _clean_item(item))

        page = custom.get("page", {})
        if isinstance(page, dict) and page.get("enabled"):
            merged_settings["page"] = _deep_merge(merged_settings["page"], _clean_page(page))

        if "latin_font" in custom:
            flags["latin_font"] = custom["latin_font"]

    return merged_settings, flags


def _build_default_settings() -> dict:
    return {
        "page": defaults.get_page_spec(),
        "title": defaults.get_title_spec(),
        "heading_1": defaults.get_heading_spec(1),
        "heading_2": defaults.get_heading_spec(2),
        "heading_3": defaults.get_heading_spec(3),
        "body": defaults.get_body_spec(),
        "table_caption": defaults.get_table_caption_spec(),
        "figure_caption": defaults.get_figure_caption_spec(),
        "reference": defaults.get_reference_spec(),
        "toc_title": defaults.get_toc_title_spec(),
        "toc_entry": defaults.get_toc_entry_spec(),
        "table_text": defaults.get_table_text_spec(),
        "header_footer": defaults.get_header_footer_spec(),
    }


def _clean_item(item: dict) -> dict:
    """从自定义格式项中提取实际值并转换为正确的 docx 类型。"""
    result = {}
    for f in ("font_name", "alignment", "line_spacing_rule"):
        if item.get(f):
            result[f] = item[f]
    if item.get("font_size_pt") is not None:
        result["font_size"] = Pt(item["font_size_pt"])
    if item.get("bold") is not None:
        result["bold"] = item["bold"]
    if item.get("line_spacing") is not None:
        result["line_spacing"] = item["line_spacing"]
    if item.get("first_line_indent") is not None:
        result["first_line_indent"] = Cm(item["first_line_indent"])
    if item.get("space_before") is not None:
        result["space_before"] = Pt(item["space_before"])
    if item.get("space_after") is not None:
        result["space_after"] = Pt(item["space_after"])
    return result


def _clean_page(page: dict) -> dict:
    """从自定义页面设置中提取实际值并转换为 Cm 类型。"""
    result = {}
    for f in ("paper_size", "orientation"):
        if page.get(f):
            result[f] = page[f]
    for f in ("margin_top", "margin_bottom", "margin_left", "margin_right",
              "header_distance", "footer_distance"):
        if page.get(f) is not None:
            result[f] = Cm(page[f])
    return result


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, val in override.items():
        if isinstance(val, dict) and key in result and isinstance(result[key], dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result
