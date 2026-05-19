"""东亚字体和拉丁字体设置"""
from lxml import etree


def set_east_asian_font(run, font_name: str) -> None:
    """设置东亚文字字体（如黑体、宋体）"""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rFonts is None:
        rFonts = etree.SubElement(
            rPr,
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts",
        )
    rFonts.set(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia",
        font_name,
    )


def set_latin_font(run, font_name: str) -> None:
    """设置拉丁文字字体（如 Times New Roman），覆盖 ascii/hAnsi/cs"""
    run.font.name = font_name
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rFonts is None:
        rFonts = etree.SubElement(
            rPr,
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts",
        )
    rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii", font_name)
    rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi", font_name)
    rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs", font_name)
