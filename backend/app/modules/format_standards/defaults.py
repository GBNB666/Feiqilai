"""护理学论文格式规范默认值"""
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ── 页面设置：A4 四边2.5cm ──
PAGE_SPEC = {
    "margin_top": Cm(2.5),
    "margin_bottom": Cm(2.5),
    "margin_left": Cm(2.5),
    "margin_right": Cm(2.5),
    "header_distance": Cm(1.5),
    "footer_distance": Cm(1.75),
    "page_width": Cm(21.0),
    "page_height": Cm(29.7),
}

# ── 标题规格（4级 + 论文标题 + 副标题 + 特殊标题）──

HEADING_SPECS = {
    1: {  # 一、黑体四号14pt加粗
        "font_name": "黑体", "font_size": Pt(14), "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT, "line_spacing": Pt(20),
        "space_before": Pt(6), "space_after": Pt(6),
    },
    2: {  # (一)宋体小四12pt加粗
        "font_name": "宋体", "font_size": Pt(12), "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT, "line_spacing": Pt(20),
        "space_before": Pt(3), "space_after": Pt(3),
    },
    3: {  # 1. 宋体小四12pt常规
        "font_name": "宋体", "font_size": Pt(12), "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT, "line_spacing": Pt(20),
        "space_before": Pt(2), "space_after": Pt(2),
    },
    4: {  # (1)宋体小四12pt常规
        "font_name": "宋体", "font_size": Pt(12), "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT, "line_spacing": Pt(20),
        "space_before": Pt(2), "space_after": Pt(2),
    },
}

TITLE_SPEC = {  # 论文标题: 黑体二号22pt居中加粗
    "font_name": "黑体", "font_size": Pt(22), "bold": True,
    "alignment": WD_ALIGN_PARAGRAPH.CENTER, "line_spacing": Pt(20), "underline": False,
}

SUBTITLE_SPEC = {  # 副标题: 宋体小三15pt居中
    "font_name": "宋体", "font_size": Pt(15), "bold": False,
    "alignment": WD_ALIGN_PARAGRAPH.CENTER,
}

SPECIAL_HEADING_SPEC = {  # 摘要/Abstract/关键词/目录/致谢/参考文献/附录: 黑体小三15pt加粗
    "font_name": "黑体", "font_size": Pt(15), "bold": True,
    "alignment": WD_ALIGN_PARAGRAPH.LEFT, "line_spacing": Pt(20),
}

BODY_SPEC = {  # 正文: 宋体小四12pt 两端对齐 1.5倍行距 首行缩进2字符
    "font_name": "宋体", "font_size": Pt(12), "bold": False,
    "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY, "line_spacing": 1.5,
    "first_line_indent": Pt(24), "space_before": Pt(0), "space_after": Pt(0),
}

CAPTION_SPEC = {  # 题注(图/表标题): 宋体小五9pt居中
    "font_name": "宋体", "font_size": Pt(9), "bold": False,
    "alignment": WD_ALIGN_PARAGRAPH.CENTER,
}

REFERENCE_SPEC = {  # 参考文献: 宋体五号10.5pt 左对齐 单倍行距
    "font_name": "宋体", "font_size": Pt(10.5), "bold": False,
    "alignment": WD_ALIGN_PARAGRAPH.LEFT, "line_spacing": 1.0,
}

HEADER_FOOTER_SPEC = {  # 页眉页脚: 宋体小五9pt居中
    "font_name": "宋体", "font_size": Pt(9), "bold": False,
    "alignment": WD_ALIGN_PARAGRAPH.CENTER,
}


# ── 查询函数 ──

def get_page_spec() -> dict:
    return dict(PAGE_SPEC)

def get_title_spec() -> dict:
    return dict(TITLE_SPEC)

def get_subtitle_spec() -> dict:
    return dict(SUBTITLE_SPEC)

def get_special_heading_spec() -> dict:
    return dict(SPECIAL_HEADING_SPEC)

def get_heading_spec(level: int) -> dict:
    spec = HEADING_SPECS.get(level)
    return dict(spec) if spec else dict(HEADING_SPECS[1])

def get_body_spec() -> dict:
    return dict(BODY_SPEC)

def get_caption_spec() -> dict:
    return dict(CAPTION_SPEC)

def get_reference_spec() -> dict:
    return dict(REFERENCE_SPEC)

def get_header_footer_spec() -> dict:
    return dict(HEADER_FOOTER_SPEC)
