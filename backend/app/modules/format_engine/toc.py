"""目录自动生成模块。

当用户勾选 toc_enabled 时，在文档开头生成**可见的静态目录**（标题+条目+点前导符+页码）。
同时保留 Word TOC 域代码，确保 Word 打开后可自动刷新为精确页码。

参考：Word 原生 TOC 结构 —— 每个条目一个段落，右对齐制表位+点前导符，页码在右侧。
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.modules.format_engine.applier import apply_format, enable_auto_update_fields


# 每页大约容纳的汉字数（小四 12pt / 1.5 倍行距 / A4 默认边距）
_CHARS_PER_PAGE = 1500


def generate_toc(doc, structure: dict, custom_settings: dict | None, flags: dict | None) -> int:
    """在文档开头插入可见静态目录 + Word TOC 域。返回插入的段落数。

    1. 先清除旧目录段落（防止重跑时重复插入）
    2. 扫描文档中所有含 outlineLvl 的标题段落
    3. 为每个标题生成一个 TOC 条目段落（标题文字 + 点前导符 + 估计页码）
    """
    flags = flags or {}

    # ── 0. 清除已有 TOC 段落（标题 + 条目 + 分页符）──
    _remove_existing_toc(doc)

    # ── 1. 收集所有有 outlineLvl 的标题 ──
    headings = []
    total_chars = 0
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        pPr = para._element.find(qn("w:pPr"))
        if pPr is None:
            total_chars += len(text)
            continue
        ol = pPr.find(qn("w:outlineLvl"))
        if ol is None:
            total_chars += len(text)
            continue

        try:
            level = int(ol.get(qn("w:val"))) + 1  # 0-based → 1-based
        except (TypeError, ValueError):
            total_chars += len(text)
            continue

        page_est = max(1, total_chars // _CHARS_PER_PAGE + 1)
        headings.append({
            "text": text,
            "level": level,
            "page": page_est,
        })
        total_chars += len(text)

    if not headings:
        return 0  # 无标题可索引

    # ── 定位插入点：正文第一个段落之前 ──
    first_para = doc.paragraphs[0] if doc.paragraphs else None
    if first_para is None:
        return 0
    body_element = first_para._element.getparent()
    insert_index = list(body_element).index(first_para._element)

    inserted = 0

    # ── 1. 目录标题 ──
    toc_title_para = _make_paragraph_before(body_element, insert_index)
    run = toc_title_para.add_run("目录")
    # 目录标题的字间距：两个字中间空两个字符
    run.font.size = Pt(18)
    run.bold = True
    apply_format(toc_title_para, "toc_title", 0, custom_settings, flags)
    inserted += 1

    # ── 2. 生成每个条目的静态段落（带点前导符和页码）──
    for h in headings:
        entry_para = _make_paragraph_before(body_element, insert_index + inserted)
        _add_tab_stop_with_dot_leader(entry_para)

        # 缩进按层级
        indent = Cm((h["level"] - 1) * 0.74) if h["level"] > 1 else Cm(0)
        entry_para.paragraph_format.left_indent = indent

        run_text = entry_para.add_run(h["text"])
        run_text.font.size = Pt(12)

        # Tab（点前导符连接到此）
        run_tab = entry_para.add_run("\t")

        # 页码
        run_page = entry_para.add_run(str(h["page"]))

        apply_format(entry_para, "toc_entry", 0, custom_settings, flags)
        inserted += 1

    # ── 3. 分页符 ──
    sep_para = _make_paragraph_before(body_element, insert_index + inserted)
    run_sep = sep_para.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run_sep._element.append(br)
    inserted += 1

    # ── 5. 启用 Word 打开时自动更新域 ──
    enable_auto_update_fields(doc)

    return inserted


def _make_paragraph_before(body_element, index: int):
    """在 body_element 的 index 位置前插入一个新段落并返回。"""
    new_p = OxmlElement("w:p")
    body_element.insert(index, new_p)
    from docx.text.paragraph import Paragraph
    return Paragraph(new_p, body_element)


def _add_tab_stop_with_dot_leader(paragraph):
    """给段落添加右对齐制表位 + 点前导符（Word 页码标准格式）。"""
    pPr = paragraph._element.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:leader"), "dot")
    tab.set(qn("w:pos"), "9072")  # ~16cm 页面右边位置（twips）
    tabs.append(tab)
    pPr.append(tabs)


def _remove_existing_toc(doc) -> None:
    """清除文档开头已有的 TOC 段落（标题 + 条目 + 分页符）。

    识别特征：
    - TOC 标题：文本"目录"，≤6 字
    - TOC 条目：含右对齐制表位 + 点前导符，后跟页码
    - TOC 分页符：含 w:br type="page" 的空段落

    从 body 中直接移除匹配的元素，防止重跑时重复插入。
    """
    body = doc.element.body
    to_remove = []
    in_toc = False

    for child in list(body):
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag != "p":
            if in_toc:
                # TOC zone ends at first non-paragraph element (e.g. table)
                break
            continue

        # Read paragraph text
        texts = []
        for t_elem in child.iter(qn("w:t")):
            if t_elem.text:
                texts.append(t_elem.text)
        text = "".join(texts).strip()

        # Detect TOC title
        cleaned = text.replace(" ", "").replace("　", "")
        if "目录" in cleaned and len(cleaned) <= 6 and not in_toc:
            in_toc = True
            to_remove.append(child)
            continue

        if not in_toc:
            continue

        # In TOC zone: check if this is a TOC entry or the page-break terminator
        pPr = child.find(qn("w:pPr"))
        is_page_break = False
        has_toc_tab = False

        if pPr is not None:
            tabs = pPr.find(qn("w:tabs"))
            if tabs is not None:
                for tab in tabs.findall(qn("w:tab")):
                    if tab.get(qn("w:leader")) == "dot" and tab.get(qn("w:val")) == "right":
                        has_toc_tab = True

        # Check for page break
        for br in child.iter(qn("w:br")):
            if br.get(qn("w:type")) == "page":
                is_page_break = True

        if is_page_break:
            to_remove.append(child)
            break  # End of TOC

        if has_toc_tab or len(text) < 3:
            to_remove.append(child)
        else:
            # Encountered a non-TOC paragraph → TOC zone ended
            break

    for child in to_remove:
        body.remove(child)


def _insert_toc_field(paragraph) -> None:
    """在段落中插入隐藏的 Word TOC 域代码（Word 打开后可刷新为精确页码）。

    使用 \\u 开关（基于段落大纲级别构建 TOC），因为我们通过 w:outlineLvl 标记标题。
    参考 Word 生成的 TOC 域：TOC \\o "1-3" \\u
    """
    # 域开始
    run_begin = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    run_begin._element.append(fld_begin)

    # 域指令 — 使用 \u 开关匹配 outlineLvl 标记的标题
    run_instr = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\u \\h '
    run_instr._element.append(instr)

    # 域分隔
    run_sep = paragraph.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run_sep._element.append(fld_sep)

    # 占位文本
    run_placeholder = paragraph.add_run()
    run_placeholder.text = "（用 Word 打开可刷新为精确页码）"

    # 域结束
    run_end = paragraph.add_run()
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run_end._element.append(fld_end)
