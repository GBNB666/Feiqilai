from docx.oxml.ns import qn
from docx.shared import Pt
from app.modules.format_standards.defaults import FONT_LATIN

# 中文字体名 → 英文名映射（Word OOXML 内部使用英文名更稳定）
CN_FONT_MAP = {
    "黑体": "SimHei",
    "宋体": "SimSun",
    "楷体": "KaiTi",
    "楷体_GB2312": "KaiTi",
    "仿宋": "FangSong",
    "仿宋_GB2312": "FangSong",
    "微软雅黑": "Microsoft YaHei",
    "SimHei": "SimHei",
    "SimSun": "SimSun",
    "KaiTi": "KaiTi",
    "FangSong": "FangSong",
    "Microsoft YaHei": "Microsoft YaHei",
}


def normalize_font_name(name: str) -> str:
    """统一字体名为英文，确保 OOXML 输出稳定。
    中文名（楷体/黑体/宋体/仿宋）→ 英文名（KaiTi/SimHei/SimSun/FangSong）
    已是英文名则保持不变。
    """
    if not name:
        return name
    return CN_FONT_MAP.get(name, name)


def set_east_asian_font(run, font_name: str) -> None:
    """设置东亚文字字体（w:eastAsia）。
    只操作 XML 属性，不调用 run.font.name 避免污染 w:ascii。
    """
    normalized = normalize_font_name(font_name)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        from lxml import etree
        rFonts = etree.SubElement(rPr, qn("w:rFonts"))
    rFonts.set(qn("w:eastAsia"), normalized)
    # 同时设置 w:cs（复杂脚本）为同一字体，覆盖特殊符号
    if not rFonts.get(qn("w:cs")):
        rFonts.set(qn("w:cs"), normalized)


def set_latin_font(run, font_name: str = FONT_LATIN) -> None:
    """设置西文字体（w:ascii + w:hAnsi + w:cs）。"""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        from lxml import etree
        rFonts = etree.SubElement(rPr, qn("w:rFonts"))
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)
    run.font.name = font_name


def apply_latin_font_to_paragraph(paragraph, font_name: str = FONT_LATIN) -> None:
    """段落中英文/数字的 run 设为拉丁字体"""
    import re
    for run in paragraph.runs:
        if re.search(r"[a-zA-Z0-9]", run.text):
            set_latin_font(run, font_name)
