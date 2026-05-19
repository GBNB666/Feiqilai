"""自定义格式设置与默认值合并逻辑"""


def merge_settings(custom: dict | None, enabled: dict | None) -> dict:
    """
    将前端传来的自定义设置与默认格式规范合并。
    enabled[field] == True → 用 custom 值
    enabled[field] == False/None → 用 default 值
    custom 为 None → 全部用默认值

    返回统一格式的 settings dict，供 applier.py 直接使用
    """
    from app.modules.format_standards.defaults import (
        get_page_spec, get_title_spec, get_subtitle_spec,
        get_special_heading_spec, get_heading_spec,
        get_body_spec, get_caption_spec, get_reference_spec, get_header_footer_spec,
    )

    result = {
        "page": get_page_spec(),
        "title": get_title_spec(),
        "subtitle": get_subtitle_spec(),
        "special_heading": get_special_heading_spec(),
        "headings": {
            1: get_heading_spec(1),
            2: get_heading_spec(2),
            3: get_heading_spec(3),
            4: get_heading_spec(4),
        },
        "body": get_body_spec(),
        "caption": get_caption_spec(),
        "reference": get_reference_spec(),
        "header_footer": get_header_footer_spec(),
        "toc_enabled": True,
    }

    if not custom:
        return result

    _merge_single(result["page"], custom.get("page"), enabled.get("page") if enabled else None)
    _merge_single(result["title"], custom.get("title"), enabled.get("title") if enabled else None)
    _merge_single(result["subtitle"], custom.get("subtitle"), enabled.get("subtitle") if enabled else None)
    _merge_single(result["special_heading"], custom.get("special_heading"), enabled.get("special_heading") if enabled else None)

    # 四级标题
    for level in [1, 2, 3, 4]:
        h_key = f"h{level}"
        custom_heading = custom.get("headings", {}).get(str(level)) or custom.get(h_key)
        enabled_heading = None
        if enabled:
            enabled_heading = enabled.get("headings", {}).get(str(level)) or enabled.get(h_key)
        if custom_heading:
            _merge_single(result["headings"][level], custom_heading, enabled_heading)

    _merge_single(result["body"], custom.get("body"), enabled.get("body") if enabled else None)
    _merge_single(result["caption"], custom.get("caption"), enabled.get("caption") if enabled else None)
    _merge_single(result["reference"], custom.get("reference"), enabled.get("reference") if enabled else None)
    _merge_single(result["header_footer"], custom.get("header_footer"), enabled.get("header_footer") if enabled else None)

    if "toc_enabled" in custom:
        result["toc_enabled"] = custom["toc_enabled"]

    return result


def _merge_single(target: dict, custom: dict | None, enabled: dict | None) -> None:
    """按字段合并单个规格到 target（原地修改）"""
    if not custom:
        return
    for key in target:
        if enabled is not None and isinstance(enabled, dict):
            if enabled.get(key, False) and key in custom:
                target[key] = custom[key]
        elif key in custom:
            target[key] = custom[key]
