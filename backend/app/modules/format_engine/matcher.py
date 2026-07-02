import re


def match_paragraph(text: str, structure: dict, matched_sections: set) -> tuple[str, int | None]:
    """Match paragraph text to paper structure. Returns (match_type, heading_level).

    match_type: "paper_title" | "heading" | "table_caption" | "figure_caption" | "body"
    """
    clean = text.strip().replace(" ", "")

    # Strategy 0: paper title
    title = structure.get("title", "")
    if title and "__title__" not in matched_sections and _is_title_match(text, title):
        matched_sections.add("__title__")
        return ("paper_title", 0)

    # Strategy 1: caption detection - must run before heading matching
    caption_type = _get_caption_type(text)
    if caption_type:
        return (caption_type, None)

    # Strategy 2: exact heading match
    for section in structure.get("sections", []):
        title_s = section.get("title", "")
        numbering = section.get("numbering", "")
        full = f"{numbering}{title_s}".strip().replace(" ", "")
        if full and full not in matched_sections and _is_title_match(text, full):
            matched_sections.add(full)
            return ("heading", section.get("level", 1))

    # Strategy 3: start_marker fallback (strict)
    # 只当 marker ≥ 4 字、出现在段落开头、且剩余字符 ≤ 15 时才匹配。
    # 避免 "研究"/"测试" 等短 marker 误伤正文段落。
    for section in structure.get("sections", []):
        title_s = section.get("title", "")
        numbering = section.get("numbering", "")
        full = f"{numbering}{title_s}".strip().replace(" ", "")
        if full in matched_sections:
            continue
        marker = section.get("start_marker", "")
        if marker and len(marker) >= 4 and clean.startswith(marker):
            remaining = len(clean) - len(marker)
            if remaining <= 15:
                matched_sections.add(full)
                return ("heading", section.get("level", 1))

    return ("body", None)


def _get_caption_type(text: str) -> str | None:
    """Detect caption type for tables and figures.
    Returns 'table_caption', 'figure_caption', or None.
    Table captions (above table): 表/Table prefix
    Figure captions (below figure): 图/Fig/Figure prefix
    Both ≤ 50 chars."""
    stripped = text.strip()
    if len(stripped) > 50:
        return None
    if re.match(r"^(?:表|Table\.?)\s*\d+", stripped):
        return "table_caption"
    if re.match(r"^(?:图|Fig(?:ure)?\.?)\s*\d+", stripped):
        return "figure_caption"
    return None


def _is_title_match(para_text: str, title: str) -> bool:
    """精确匹配标题：只有段落和标题完全一致，或段落以标题开头且只多少量字符时才算匹配。

    之前条件太松（≤30字且包含标题词就匹配），导致正文段落（如"本研究采用…"）
    被错误当作标题，从而全部套上标题字体（黑体）。
    """
    clean_para = para_text.strip().replace(" ", "")
    clean_title = title.strip().replace(" ", "")
    if not clean_para or not clean_title:
        return False

    # 1. 完全一致
    if clean_para == clean_title:
        return True

    # 2. 以标题开头且多出来的字符 ≤ 5 个（如 "一、研究背景" vs "一、研究背景与意义"）
    #    同时要求标题长度 ≥ 3，避免 "研究"/"方法" 等短词误伤正文
    if len(clean_title) >= 3 and clean_para.startswith(clean_title):
        extra = len(clean_para) - len(clean_title)
        if extra <= 5:
            return True

    # 3. 不再允许"包含匹配"——之前 ≤30字且包含标题词的条件太宽，已移除
    return False


def is_in_reference_zone(text: str, references_found: bool) -> bool:
    """Detect entry into reference zone."""
    if "参考文献" in text.strip().replace(" ", ""):
        return True
    return references_found


def _looks_like_reference_entry(text: str) -> bool:
    """Check if text looks like a reference/citation entry.

    Reference entry patterns (any match = reference entry):
    1. Starts with [N], e.g. [1], [12]
    2. Contains journal/thesis markers: [J], [M], [D], [C], [N], [EB/OL] etc.
    3. English author + year pattern, e.g. "Smith, J. (2020)"
    4. Starts with number-dot, e.g. "1. Smith..."
    """
    stripped = text.strip()
    if not stripped:
        return False

    # [1] xxx pattern (most common in Chinese papers)
    if re.match(r"^\[\d+\]", stripped):
        return True

    # Contains reference markers [J], [M], [D], [C], [N], [EB/OL], [P], [S] etc.
    if re.search(r"\[[JMNDCPS][/]?[A-Za-z]*\]|\[EB/OL\]|\[R\]|\[G\]|\[Z\]|\[A\]", stripped):
        return True

    # English author + year: Smith, J. (2020) or Smith J (2020)
    if re.match(r"^[A-Z][a-z]+[,]?\s+[A-Z]\.?\s*[,(]", stripped):
        if re.search(r"\d{4}", stripped):
            return True

    # Number-dot start (some journal formats): "1. Smith J, et al. ..."
    if re.match(r"^\d+\.\s+[A-Z一-鿿]", stripped):
        return True

    # DOI marker (doi: or doi.org/)
    if "doi:" in stripped.lower() or "doi.org/" in stripped.lower():
        return True

    return False


def is_equation_paragraph(text: str) -> bool:
    """检测段落是否为独立公式段落。

    判断条件（参考 docx-thesis-format 的检测逻辑）：
    1. 中文字符少于 4 个（排除"正文里顺带提到公式"的情况）
    2. 包含数学符号特征
    3. 文本长度适中（不过短不过长）
    """
    clean = text.strip()
    if not clean or len(clean) < 3 or len(clean) > 200:
        return False

    # 统计中文字符数
    chinese_chars = len(re.findall(r"[一-鿿]", clean))
    if chinese_chars >= 4:
        return False  # 中文太多，是正文

    # 数学符号特征（至少匹配 2 个才算公式）
    math_patterns = [
        r"[+\-*/=<>≤≥±×÷∫∑∏√∞∂∇]",
        r"\\[a-zA-Z]+",          # LaTeX 命令
        r"[α-ωΑ-Ω]",            # 希腊字母
        r"[\^_]\{[^}]+\}",       # 上下标
        r"\b[ds]in\b|cos\b|tan\b|log\b|ln\b|exp\b|lim\b|max\b|min\b",  # 数学函数
        r"\d+\.\d+(?=[+\-*/)])",  # 数学中的小数
    ]
    math_score = sum(1 for p in math_patterns if re.search(p, clean, re.IGNORECASE))

    # 编号特征：以括号编号开头或结尾
    has_number = bool(re.match(r"^[（(]\s*\d+[-.]\d+\s*[）)]", clean) or
                     re.search(r"[（(]\s*\d+[-.]\d+\s*[）)]$", clean))

    return math_score >= 2 or has_number


def is_reference_zone_end(text: str, structure: dict) -> bool:
    """Detect if we've left the reference zone.

    Uses "doesn't look like a reference entry" logic instead of relying
    on AI-detected section structure. If a paragraph doesn't match any
    reference entry pattern, we consider the reference zone ended.
    """
    return not _looks_like_reference_entry(text)
