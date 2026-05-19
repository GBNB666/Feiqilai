"""格式应用器 — 将格式规范应用到 python-docx 段落"""
import re
from docx.oxml.ns import qn
from docx.shared import Pt
from app.modules.format_standards.defaults import (
    get_page_spec,
    get_title_spec,
    get_subtitle_spec,
    get_special_heading_spec,
    get_heading_spec,
    get_body_spec,
    get_caption_spec,
    get_reference_spec,
    get_header_footer_spec,
)
from app.modules.format_standards.fonts import set_east_asian_font, set_latin_font
from app.modules.format_standards.custom import merge_settings


def apply_page_settings(doc, custom: dict | None = None, enabled: dict | None = None):
    """应用页面设置到文档所有节"""
    merged = merge_settings(custom, enabled)
    page = merged["page"]

    for section in doc.sections:
        section.top_margin = page["margin_top"]
        section.bottom_margin = page["margin_bottom"]
        section.left_margin = page["margin_left"]
        section.right_margin = page["margin_right"]
        section.header_distance = page["header_distance"]
        section.footer_distance = page["footer_distance"]
        section.page_width = page.get("page_width", section.page_width)
        section.page_height = page.get("page_height", section.page_height)


def apply_format(
    para,
    match_type: str,
    level: int | None,
    custom_settings: dict | None = None,
    enabled_flags: dict | None = None,
    in_reference_section: bool = False,
) -> None:
    """
    根据匹配类型应用对应格式。

    match_type: "paper_title" | "subtitle" | "special_heading" | "heading" | "body"
    """
    merged = merge_settings(custom_settings, enabled_flags)

    if match_type == "paper_title":
        spec = merged["title"]
        _apply_spec(para, spec, is_heading=True)
    elif match_type == "subtitle":
        spec = merged["subtitle"]
        _apply_spec(para, spec, is_heading=False)
    elif match_type == "special_heading":
        spec = merged["special_heading"]
        _apply_spec(para, spec, is_heading=True)
    elif match_type == "heading":
        spec = merged["headings"].get(level, merged["headings"][1])
        _apply_spec(para, spec, is_heading=True)
    elif match_type == "body":
        text = para.text.strip()
        if re.match(r"^(图|表)\s*\d+", text):
            spec = merged["caption"]
            _apply_spec(para, spec, is_heading=False)
        elif in_reference_section:
            spec = merged["reference"]
            _apply_spec(para, spec, is_heading=False)
        else:
            spec = merged["body"]
            _apply_spec(para, spec, is_heading=False)
            # 英文数字设 Times New Roman
            _apply_latin_font_to_runs(para)


def _normalize_alignment(value):
    """将字符串对齐值转为 WD_ALIGN_PARAGRAPH 枚举"""
    if value is None:
        return None
    if isinstance(value, str):
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        mapping = {v.name.lower(): v for v in WD_ALIGN_PARAGRAPH}
        return mapping.get(value.lower(), None)
    return value


def _apply_spec(para, spec: dict, is_heading: bool) -> None:
    """将格式规格应用到段落及其所有 run"""
    pf = para.paragraph_format
    alignment = spec.get("alignment")
    if alignment is not None:
        pf.alignment = _normalize_alignment(alignment)

    if "line_spacing" in spec:
        pf.line_spacing = spec["line_spacing"]
    pf.first_line_indent = spec.get("first_line_indent", Pt(0))
    if "space_before" in spec:
        pf.space_before = spec["space_before"]
    if "space_after" in spec:
        pf.space_after = spec["space_after"]

    for run in para.runs:
        font_name = spec.get("font_name", "")
        if font_name:
            run.font.name = font_name
            set_east_asian_font(run, font_name)

        if "font_size" in spec:
            run.font.size = spec["font_size"]
        if "bold" in spec:
            run.font.bold = spec["bold"]
        if spec.get("underline") is False:
            run.font.underline = False

    # 标题末尾禁止标点
    if is_heading:
        _strip_trailing_punctuation(para)


def _apply_latin_font_to_runs(para) -> None:
    """正文段落中的英文数字 run 设置为 Times New Roman"""
    for run in para.runs:
        text = run.text
        if text and any(c.isascii() and (c.isalpha() or c.isdigit()) for c in text):
            set_latin_font(run, "Times New Roman")


def _strip_trailing_punctuation(para) -> None:
    """移除标题末尾的标点符号"""
    if para.runs:
        last_run = para.runs[-1]
        text = last_run.text
        if text:
            last_run.text = text.rstrip("。，、；：！？. ,;:!?")


def apply_header_footer(doc, paper_title: str, custom: dict | None = None, enabled: dict | None = None) -> None:
    """应用页眉页脚格式"""
    merged = merge_settings(custom, enabled)
    spec = merged["header_footer"]

    for section in doc.sections:
        header = section.header
        if not header.is_linked_to_previous:
            for para in header.paragraphs:
                _apply_spec(para, spec, is_heading=False)
                if para.runs:
                    para.runs[0].text = paper_title or ""

        footer = section.footer
        if not footer.is_linked_to_previous:
            for para in footer.paragraphs:
                _apply_spec(para, spec, is_heading=False)


def reset_run_color(para) -> None:
    """将所有 run 的文字颜色重置为黑色"""
    for run in para.runs:
        if run.font.color and run.font.color.rgb:
            run.font.color.rgb = None
