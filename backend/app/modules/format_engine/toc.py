"""目录生成"""
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.modules.format_standards.fonts import set_east_asian_font


def remove_old_toc(doc) -> None:
    """检测并移除旧目录"""
    body = doc.element.body
    toc_start = None
    toc_end = None

    paragraphs = doc.paragraphs
    for i, para in enumerate(paragraphs[:20]):
        if "目录" in para.text.strip():
            toc_start = i
            break

    if toc_start is not None:
        for i in range(toc_start + 1, min(len(paragraphs), toc_start + 50)):
            text = paragraphs[i].text.strip()
            if text and "目录" not in text and (
                text.startswith("一、") or text.startswith("摘要") or text.startswith("Abstract")
            ):
                toc_end = i
                break

    if toc_start is not None and toc_end is not None:
        for i in range(toc_end - 1, toc_start - 1, -1):
            para = paragraphs[i]
            para._element.getparent().remove(para._element)


def generate_toc(doc, structure: dict, custom: dict | None = None, enabled: dict | None = None) -> None:
    """在正文第一个标题前插入目录"""
    from app.modules.format_standards.defaults import SPECIAL_HEADING_SPEC, BODY_SPEC
    from app.modules.format_standards.fonts import set_east_asian_font

    # 找到第一个正文标题的位置
    insert_index = 0
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        sections = structure.get("sections", [])
        for sec in sections[:3]:
            numbering = sec.get("numbering", "")
            title = sec.get("title", "")
            full = f"{numbering}{title}"
            if full and full in text:
                insert_index = i
                break
        if insert_index > 0:
            break

    if insert_index == 0:
        return

    # 在插入点前插入目录
    toc_title_para = doc.paragraphs[insert_index]._element
    parent = toc_title_para.getparent()

    # 目录标题
    title_para = _make_paragraph(doc, "目录", SPECIAL_HEADING_SPEC, is_heading=True)
    parent.insert(parent.index(toc_title_para), title_para._element)

    # 目录项
    sections = structure.get("sections", [])
    for sec in sections:
        level = sec.get("level", 1)
        numbering = sec.get("numbering", "")
        title = sec.get("title", "")
        entry_text = f"{numbering}{title}"

        indent = Pt(24 * (level - 1)) if level > 1 else Pt(0)
        para = doc.add_paragraph()
        run = para.add_run(f"{entry_text} ............ [页码]")
        run.font.size = Pt(12)
        run.font.name = "宋体"
        set_east_asian_font(run, "宋体")
        para.paragraph_format.first_line_indent = indent

        parent.insert(parent.index(toc_title_para), para._element)

    # 目录和正文之间加空行
    spacer = doc.add_paragraph()
    parent.insert(parent.index(toc_title_para), spacer._element)


def _make_paragraph(doc, text: str, spec: dict, is_heading: bool = False):
    """创建一个格式化的段落"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.name = spec.get("font_name", "宋体")
    run.font.size = spec.get("font_size", Pt(12))
    run.font.bold = spec.get("bold", False)
    set_east_asian_font(run, spec.get("font_name", "宋体"))
    para.paragraph_format.alignment = spec.get("alignment", WD_ALIGN_PARAGRAPH.LEFT)
    if "line_spacing" in spec:
        para.paragraph_format.line_spacing = spec["line_spacing"]
    return para
