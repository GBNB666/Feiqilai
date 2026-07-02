"""FORMAT_RULES: 所有格式属性硬编码在此，不依赖 AI 猜测。"""
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

FONT_HEI = "SimHei"
FONT_SONG = "SimSun"
FONT_LATIN = "Times New Roman"

FORMAT_RULES = {
    "paper_title": {
        "font_name": FONT_HEI,
        "font_size": Pt(16),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "color": RGBColor(0, 0, 0),
        "line_spacing": Pt(20),
        "line_spacing_rule": "EXACTLY",
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "heading_1": {
        "font_name": FONT_HEI,
        "font_size": Pt(16),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "color": RGBColor(0, 0, 0),
        "line_spacing": Pt(20),
        "line_spacing_rule": "EXACTLY",
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "heading_2": {
        "font_name": FONT_HEI,
        "font_size": Pt(14),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "color": RGBColor(0, 0, 0),
        "line_spacing": Pt(20),
        "line_spacing_rule": "EXACTLY",
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "heading_3": {
        "font_name": FONT_HEI,
        "font_size": Pt(12),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "color": RGBColor(0, 0, 0),
        "line_spacing": Pt(20),
        "line_spacing_rule": "EXACTLY",
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "body": {
        "font_name": FONT_SONG,
        "font_size": Pt(12),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "color": RGBColor(0, 0, 0),
        "line_spacing": 1.5,
        "line_spacing_rule": None,
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": Cm(0.74),
    },
    "table_caption": {
        "font_name": FONT_HEI,
        "font_size": Pt(10.5),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "color": RGBColor(0, 0, 0),
        "line_spacing": None,
        "line_spacing_rule": None,
        "space_before": Pt(0),
        "space_after": Pt(6),
        "first_line_indent": None,
    },
    "figure_caption": {
        "font_name": FONT_HEI,
        "font_size": Pt(10.5),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "color": RGBColor(0, 0, 0),
        "line_spacing": None,
        "line_spacing_rule": None,
        "space_before": Pt(6),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "reference": {
        "font_name": FONT_SONG,
        "font_size": Pt(10.5),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "color": RGBColor(0, 0, 0),
        "line_spacing": 1.0,
        "line_spacing_rule": None,
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
        "hanging_indent": Cm(0.74),  # 悬挂缩进 2 字符
    },
    "toc_title": {
        "font_name": FONT_HEI,
        "font_size": Pt(16),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "color": RGBColor(0, 0, 0),
        "line_spacing": 1.5,
        "line_spacing_rule": None,
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "toc_entry": {
        "font_name": FONT_SONG,
        "font_size": Pt(12),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "color": RGBColor(0, 0, 0),
        "line_spacing": 1.5,
        "line_spacing_rule": None,
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "header_footer": {
        "font_name": FONT_SONG,
        "font_size": Pt(9),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "color": RGBColor(0, 0, 0),
        "line_spacing": None,
        "line_spacing_rule": None,
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
    },
    "table_text": {
        "font_name": FONT_SONG,
        "font_size": Pt(10.5),
        "bold": False,
        "color": RGBColor(0, 0, 0),
    },
    "equation": {
        "font_name": FONT_LATIN,
        "font_size": Pt(12),
        "bold": False,
        "alignment": None,  # 公式段落特殊处理：居中制表位
        "color": RGBColor(0, 0, 0),
        "line_spacing": Pt(22),
        "line_spacing_rule": "EXACTLY",
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": None,
        # 公式编号格式
        "number_format": "({chapter}-{index})",
        "center_tab_twips": 4500,   # 居中制表位（约 8cm）
        "right_tab_twips": 9000,    # 右对齐制表位（约 16cm）
    },
}


def get_rule(match_type: str, level: int | None = None) -> dict:
    """根据匹配类型和标题级别返回硬编码格式规则。"""
    if match_type == "heading" and level is not None:
        key = f"heading_{level}"
        return FORMAT_RULES.get(key, FORMAT_RULES["body"])
    return FORMAT_RULES.get(match_type, FORMAT_RULES["body"])
