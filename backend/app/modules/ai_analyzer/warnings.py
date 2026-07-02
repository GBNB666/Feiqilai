import re
from app.shared.schemas import FormatWarnings


def detect_warnings(structure: dict) -> FormatWarnings:
    return FormatWarnings(
        missing_abstract=not structure.get("has_abstract", False),
        missing_toc=not structure.get("has_toc", False),
        missing_references=not structure.get("has_references", False),
        missing_figure_labels=_check_missing_labels(structure, "图"),
        missing_table_labels=_check_missing_labels(structure, "表"),
        conflicting_headings=_check_conflicting_headings(structure),
    )


FIG_PATTERN = re.compile(r"图\d+")
TABLE_PATTERN = re.compile(r"表\d+")


def _check_missing_labels(structure: dict, label_type: str) -> bool:
    """检查章节中有图/表但缺少图序/表序文字。"""
    pattern = FIG_PATTERN if label_type == "图" else TABLE_PATTERN
    field = "has_figures" if label_type == "图" else "has_tables"

    for section in structure.get("sections", []):
        if section.get(field, False):
            summary = section.get("content_summary", "")
            if not pattern.search(summary):
                return True
    return False


def _check_conflicting_headings(structure: dict) -> bool:
    """检查同级标题编号是否跳跃。"""
    numbering_patterns = {
        1: re.compile(r"^([一二三四五六七八九十]+)、"),
        2: re.compile(r"^（([一二三四五六七八九十]+)）"),
        3: re.compile(r"^(\d+)\."),
        4: re.compile(r"^\((\d+)\)"),
    }

    cn_nums = {
        "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    }

    sections_by_level: dict[int, list[int]] = {}
    for section in structure.get("sections", []):
        level = section.get("level", 0)
        if level <= 0:
            continue
        numbering = section.get("numbering", "")
        pattern = numbering_patterns.get(level)
        if not pattern:
            continue
        m = pattern.match(numbering)
        if not m:
            continue
        raw = m.group(1)
        if level in (1, 2):
            num = cn_nums.get(raw)
            if num is None:
                continue
        else:
            num = int(raw)

        sections_by_level.setdefault(level, []).append(num)

    for level, nums in sections_by_level.items():
        for i in range(1, len(nums)):
            if nums[i] != nums[i - 1] + 1:
                return True

    return False
