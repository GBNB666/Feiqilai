"""格式警告检测"""
import re


def detect_warnings(structure: dict) -> dict:
    """检测论文格式问题，返回警告字典"""
    warnings = {
        "missing_abstract": False,
        "missing_abstract_en": False,
        "missing_toc": False,
        "missing_references": False,
        "missing_acknowledgement": False,
        "missing_figure_labels": [],
        "missing_table_labels": [],
        "conflicting_headings": [],
    }

    if not structure:
        return warnings

    warnings["missing_abstract"] = not structure.get("has_abstract", False)
    warnings["missing_abstract_en"] = not structure.get("has_abstract_en", False)
    warnings["missing_toc"] = not structure.get("has_toc", False)
    warnings["missing_references"] = not structure.get("has_references", False)
    warnings["missing_acknowledgement"] = not structure.get("has_acknowledgement", False)

    sections = structure.get("sections", [])
    for i, sec in enumerate(sections):
        content = sec.get("content_summary", "") + sec.get("start_marker", "")
        if sec.get("has_figures") and not re.search(r"图\s*\d+", content):
            warnings["missing_figure_labels"].append(
                f"第{i+1}节「{sec.get('numbering','')}{sec.get('title','')}」: 含图但缺图序"
            )
        if sec.get("has_tables") and not re.search(r"表\s*\d+", content):
            warnings["missing_table_labels"].append(
                f"第{i+1}节「{sec.get('numbering','')}{sec.get('title','')}」: 含表但缺表序"
            )

    levels = [s.get("level", 0) for s in sections if s.get("level", 0) > 0]
    for i in range(1, len(levels)):
        if levels[i] > levels[i-1] + 1:
            warnings["conflicting_headings"].append(
                f"第{i+1}节标题级别从{levels[i-1]}跳跃到{levels[i]}"
            )

    return warnings
