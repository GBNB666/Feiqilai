"""论文格式标准定义模块"""
from dataclasses import dataclass
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

FONT_HEITI = "黑体"
FONT_SONGTI = "宋体"

# Page settings
PAGE_SPEC = {
    "margin_top_cm": 2.54,
    "margin_bottom_cm": 2.54,
    "margin_left_cm": 3.17,
    "margin_right_cm": 3.17,
    "header_distance_cm": 1.5,
    "footer_distance_cm": 1.75,
}

# Heading specs: (size_pt, bold, alignment, space_before, space_after)
HEADING_SPECS = {
    1: {"size": Pt(16), "bold": True, "align": WD_ALIGN_PARAGRAPH.CENTER, "space_before": Pt(12), "space_after": Pt(6)},
    2: {"size": Pt(14), "bold": True, "align": WD_ALIGN_PARAGRAPH.LEFT, "space_before": Pt(10), "space_after": Pt(4)},
    3: {"size": Pt(12), "bold": True, "align": WD_ALIGN_PARAGRAPH.LEFT, "space_before": Pt(8), "space_after": Pt(4)},
}

# Body: 宋体 12pt, justify, 1.5 line spacing, first-line indent 2 chars (24pt at 12pt)
BODY_SPEC = {
    "font_name": FONT_SONGTI,
    "font_name_east": FONT_SONGTI,
    "size": Pt(12),
    "bold": False,
    "align": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "line_spacing": 1.5,
    "first_line_indent": Pt(24),
    "space_before": Pt(0),
    "space_after": Pt(0),
}

# Caption (figure/table): 宋体 10.5pt, center
CAPTION_SPEC = {
    "font_name": FONT_SONGTI,
    "font_name_east": FONT_SONGTI,
    "size": Pt(10.5),
    "bold": False,
    "align": WD_ALIGN_PARAGRAPH.CENTER,
    "line_spacing": 1.5,
    "first_line_indent": None,
    "space_before": Pt(2),
    "space_after": Pt(2),
}

# Reference entry: 宋体 10.5pt, single line spacing
REFERENCE_SPEC = {
    "font_name": FONT_SONGTI,
    "font_name_east": FONT_SONGTI,
    "size": Pt(10.5),
    "bold": False,
    "align": WD_ALIGN_PARAGRAPH.LEFT,
    "line_spacing": 1.0,
    "first_line_indent": None,
    "space_before": Pt(0),
    "space_after": Pt(0),
}

# Header/footer: 宋体 9pt, center
HEADER_FOOTER_SPEC = {
    "font_name": FONT_SONGTI,
    "font_name_east": FONT_SONGTI,
    "size": Pt(9),
    "bold": False,
}


def apply_page_settings(doc):
    """Apply standard page margins to all sections."""
    for section in doc.sections:
        section.top_margin = Cm(PAGE_SPEC["margin_top_cm"])
        section.bottom_margin = Cm(PAGE_SPEC["margin_bottom_cm"])
        section.left_margin = Cm(PAGE_SPEC["margin_left_cm"])
        section.right_margin = Cm(PAGE_SPEC["margin_right_cm"])
        section.header_distance = Cm(PAGE_SPEC["header_distance_cm"])
        section.footer_distance = Cm(PAGE_SPEC["footer_distance_cm"])


def _apply_para_spec(para, spec: dict):
    """Apply font, alignment, spacing, indent to a paragraph."""
    pf = para.paragraph_format
    pf.alignment = spec["align"]
    pf.line_spacing = spec["line_spacing"]
    pf.space_before = spec.get("space_before", Pt(0))
    pf.space_after = spec.get("space_after", Pt(0))
    if spec.get("first_line_indent") is not None:
        pf.first_line_indent = spec["first_line_indent"]

    for run in para.runs:
        run.font.size = spec["size"]
        run.font.bold = spec.get("bold", False)
        _set_run_east_font(run, spec.get("font_name_east", spec.get("font_name", FONT_SONGTI)))


def apply_heading_format(para, level: int):
    """Apply heading formatting to a paragraph."""
    spec = HEADING_SPECS.get(level, HEADING_SPECS[1])
    pf = para.paragraph_format
    pf.alignment = spec["align"]
    pf.line_spacing = 1.5
    pf.space_before = spec["space_before"]
    pf.space_after = spec["space_after"]
    pf.first_line_indent = None

    for run in para.runs:
        run.font.name = FONT_HEITI
        run.font.size = spec["size"]
        run.font.bold = spec["bold"]
        _set_run_east_font(run, FONT_HEITI)


def apply_body_format(para):
    """Apply body text formatting."""
    _apply_para_spec(para, BODY_SPEC)


def apply_caption_format(para):
    """Apply figure/table caption formatting."""
    _apply_para_spec(para, CAPTION_SPEC)


def is_caption_paragraph(text: str) -> bool:
    """Detect if a paragraph is a figure/table caption."""
    t = text.strip()
    return t.startswith("图") or t.startswith("表") or t.startswith("Figure") or t.startswith("Table")


def _set_run_east_font(run, font_name: str):
    """Set East-Asian font on a run element."""
    try:
        from lxml import etree
        rPr = run._element.get_or_add_rPr()
        nsmap = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        rFonts = rPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        if rFonts is None:
            rFonts = etree.SubElement(rPr, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", font_name)
    except Exception:
        pass
