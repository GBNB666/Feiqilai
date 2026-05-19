"""段落→章节匹配逻辑（排版引擎和预览服务共用）"""
import re

SPECIAL_KEYWORDS = ["摘要", "Abstract", "关键词", "Key words", "目录", "参考文献", "致谢", "附录"]
BODY_SIGNAL_WORDS = ["本文", "研究", "目前", "近年来", "随着", "通过"]


def match_paragraph(
    text: str,
    structure: dict,
    matched_sections: set,
) -> tuple[str, int | None]:
    """
    匹配段落文本到论文章节。

    返回: (匹配类型, 标题级别或None)
    匹配类型: "paper_title" | "subtitle" | "special_heading" | "heading" | "body"
    """
    clean = text.strip()

    # 跳过目录条目（含连续点号或制表符前导符的页码行）
    if _is_toc_entry(clean):
        return ("body", None)

    # Strategy 0: 论文标题
    paper_title = structure.get("title", "")
    if paper_title and "__title__" not in matched_sections:
        if is_title_match(clean, paper_title):
            matched_sections.add("__title__")
            return ("paper_title", 0)

    # Strategy 0b: 副标题
    subtitle = structure.get("subtitle")
    if subtitle and "__subtitle__" not in matched_sections:
        if is_title_match(clean, subtitle):
            matched_sections.add("__subtitle__")
            return ("subtitle", 0)

    # Strategy 0c: 特殊标题 — 仅当段落以关键词开头且为短标题时匹配
    for kw in SPECIAL_KEYWORDS:
        if kw not in matched_sections and len(clean) <= 30 and clean.startswith(kw):
            matched_sections.add(kw)
            return ("special_heading", 0)

    # Strategy 1: 章节标题精确匹配（编号+标题）
    sections = structure.get("sections", [])
    for section in sections:
        numbering = section.get("numbering", "")
        title = section.get("title", "")
        full_title = f"{numbering}{title}" if numbering else title

        if full_title and full_title not in matched_sections:
            if is_title_match(clean, full_title):
                matched_sections.add(full_title)
                return ("heading", section.get("level", 1))

    # Strategy 2: start_marker 兜底
    for section in sections:
        numbering = section.get("numbering", "")
        title = section.get("title", "")
        full_title = f"{numbering}{title}" if numbering else title

        if full_title in matched_sections:
            continue

        marker = section.get("start_marker", "")
        if marker and len(marker) >= 6 and marker in clean:
            if not _is_body_signal(marker):
                matched_sections.add(full_title)
                return ("heading", section.get("level", 1))

    return ("body", None)


def is_title_match(para_text: str, title: str) -> bool:
    """检查段落文本是否匹配某个标题"""
    clean_para = para_text.strip().replace(" ", "").replace("\t", "")
    clean_title = title.strip().replace(" ", "").replace("\t", "")

    if not clean_para or not clean_title:
        return False
    if clean_para == clean_title:
        return True
    if clean_para.startswith(clean_title) and len(clean_para) - len(clean_title) <= 20:
        return True
    if len(clean_para) <= 30 and clean_para.startswith(clean_title):
        return True
    return False


def _is_body_signal(text: str) -> bool:
    """检查文本是否像正文开头而非标题"""
    for word in BODY_SIGNAL_WORDS:
        if text.startswith(word):
            return True
    return False


def is_table_paragraph(para) -> bool:
    """检查段落是否在表格内"""
    parent = para._element.getparent()
    if parent is None:
        return False
    tag = parent.tag.split("}")[-1] if "}" in parent.tag else parent.tag
    return tag == "tc"


def is_image_paragraph(para) -> bool:
    """检查段落是否包含图片"""
    xml = para._element.xml
    return "wp:inline" in xml or "wp:anchor" in xml or "a:blip" in xml


def is_caption_text(text: str) -> bool:
    """检查文本是否是图/表题注"""
    clean = text.strip()
    return bool(re.match(r"^(图|表|Figure|Table)\s*\d+", clean))


def _is_toc_entry(text: str) -> bool:
    """检查是否是目录条目（含连续点号或页码）"""
    if re.search(r"\.{3,}", text):
        return True
    if re.search(r"…{2,}", text):
        return True
    if re.search(r"\[页码\]|\d+\s*$", text) and len(text) > 40:
        return True
    return False


def is_toc_paragraph(text: str) -> bool:
    """检查是否是目录相关段落"""
    return "目录" in text.strip()
