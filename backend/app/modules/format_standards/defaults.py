from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ── 中文字号 → pt ──────────────────────────────────

CN_FONT_SIZE_MAP = {
    "初号": 42, "小初": 36,
    "一号": 26, "小一": 24,
    "二号": 22, "小二": 18,
    "三号": 16, "小三": 15,
    "四号": 14, "小四": 12,
    "五号": 10.5, "小五": 9,
}

# ── 字体名称常量 ─────────────────────────────────────

FONT_HEI = "SimHei"
FONT_SONG = "SimSun"
FONT_KAI = "KaiTi"
FONT_FANG = "FangSong"
FONT_YAHEI = "Microsoft YaHei"
FONT_LATIN = "Times New Roman"
FONT_ARIAL = "Arial"

# ── 获取函数 ────────────────────────────────────────

def get_page_spec() -> dict:
    return {
        "paper_size": "A4",
        "orientation": "portrait",
        "margin_top": Cm(2.54),
        "margin_bottom": Cm(2.54),
        "margin_left": Cm(3.17),
        "margin_right": Cm(3.17),
        "header_distance": Cm(1.5),
        "footer_distance": Cm(1.75),
    }


def get_title_spec() -> dict:
    """论文标题: 黑体三号16pt居中加粗"""
    return {
        "font_name": FONT_HEI,
        "font_size": Pt(16),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "line_spacing": Pt(20),
        "line_spacing_rule": "EXACTLY",
    }


def get_heading_spec(level: int) -> dict:
    """标题1-3级
    一级: 黑体三号16pt加粗居中
    二级: 黑体四号14pt加粗左对齐
    三级: 黑体小四12pt加粗左对齐
    """
    specs = {
        1: {"font_name": FONT_HEI, "font_size": Pt(16), "bold": True, "alignment": WD_ALIGN_PARAGRAPH.CENTER},
        2: {"font_name": FONT_HEI, "font_size": Pt(14), "bold": True, "alignment": WD_ALIGN_PARAGRAPH.LEFT},
        3: {"font_name": FONT_HEI, "font_size": Pt(12), "bold": True, "alignment": WD_ALIGN_PARAGRAPH.LEFT},
    }
    base = specs.get(level, specs[3])
    return {**base, "line_spacing": Pt(20), "line_spacing_rule": "EXACTLY"}


def get_body_spec() -> dict:
    """正文: 宋体小四12pt, 1.5倍行距, 首行缩进2字符, 两端对齐, 段前0段后0"""
    return {
        "font_name": FONT_SONG,
        "font_size": Pt(12),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "line_spacing": 1.5,
        "first_line_indent": Cm(0.74),
        "space_before": Pt(0),
        "space_after": Pt(0),
    }


def get_table_caption_spec() -> dict:
    """表注（表格上方）: 黑体五号10.5pt居中加粗, 段后6pt与表格分隔"""
    return {
        "font_name": FONT_HEI,
        "font_size": Pt(10.5),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(0),
        "space_after": Pt(6),
    }


def get_figure_caption_spec() -> dict:
    """图注（图片下方）: 黑体五号10.5pt居中加粗, 段前6pt与图片分隔"""
    return {
        "font_name": FONT_HEI,
        "font_size": Pt(10.5),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(6),
        "space_after": Pt(0),
    }


def get_reference_spec() -> dict:
    """参考文献条目: 宋体五号10.5pt, 左对齐, 单倍行距, 段前0段后0, 无缩进"""
    return {
        "font_name": FONT_SONG,
        "font_size": Pt(10.5),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "line_spacing": 1.0,
        "space_before": Pt(0),
        "space_after": Pt(0),
    }


def get_toc_title_spec() -> dict:
    """目录标题: 黑体三号16pt居中加粗, 1.5倍行距"""
    return {
        "font_name": FONT_HEI,
        "font_size": Pt(16),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "line_spacing": 1.5,
    }


def get_toc_entry_spec() -> dict:
    """目录条目: 宋体小四12pt, 1.5倍行距"""
    return {
        "font_name": FONT_SONG,
        "font_size": Pt(12),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "line_spacing": 1.5,
    }


def get_header_footer_spec() -> dict:
    """页眉/页脚: 宋体小五9pt居中"""
    return {
        "font_name": FONT_SONG,
        "font_size": Pt(9),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
    }


def get_table_text_spec() -> dict:
    """表格文字: 宋体五号10.5pt, 不加粗"""
    return {
        "font_name": FONT_SONG,
        "font_size": Pt(10.5),
        "bold": False,
    }


# ── 商业计划书模板预设 ──────────────────────────

BUSINESS_PLAN_SPECS = {
    "page": {
        "paper_size": "A4",
        "orientation": "portrait",
        "margin_top": Cm(2.54),
        "margin_bottom": Cm(2.54),
        "margin_left": Cm(3.17),
        "margin_right": Cm(3.17),
        "header_distance": Cm(1.5),
        "footer_distance": Cm(1.75),
    },
    "title": {
        "font_name": FONT_HEI,
        "font_size": Pt(22),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
    },
    "heading_1": {
        "font_name": FONT_HEI,
        "font_size": Pt(16),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(6),
        "space_after": Pt(6),
    },
    "heading_2": {
        "font_name": FONT_HEI,
        "font_size": Pt(15),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
    },
    "heading_3": {
        "font_name": FONT_KAI,
        "font_size": Pt(14),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "first_line_indent": Cm(0.74),
    },
    "body": {
        "font_name": FONT_SONG,
        "font_size": Pt(12),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "line_spacing": 1.5,
        "first_line_indent": Cm(0.74),
    },
    "table_caption": {
        "font_name": FONT_HEI,
        "font_size": Pt(10.5),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_after": Pt(6),
    },
    "figure_caption": {
        "font_name": FONT_HEI,
        "font_size": Pt(10.5),
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(6),
    },
    "reference": {
        "font_name": FONT_SONG,
        "font_size": Pt(10.5),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "line_spacing": 1.0,
    },
    "header_footer": {
        "font_name": FONT_SONG,
        "font_size": Pt(9),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
    },
}
