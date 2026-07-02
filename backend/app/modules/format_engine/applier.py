import re
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor, Length
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from app.modules.format_engine.rules import FORMAT_RULES, FONT_SONG, FONT_LATIN, FONT_HEI, get_rule
from app.modules.format_standards import defaults
from app.modules.format_standards.fonts import set_east_asian_font, set_latin_font, normalize_font_name


def apply_page_settings(doc, custom_page: dict | None = None):
    """应用页面边距等设置。"""
    margin_top = Cm(2.54)
    margin_bottom = Cm(2.54)
    margin_left = Cm(3.17)
    margin_right = Cm(3.17)

    if custom_page and custom_page.get("enabled"):
        margin_top = _cm(custom_page.get("margin_top")) or margin_top
        margin_bottom = _cm(custom_page.get("margin_bottom")) or margin_bottom
        margin_left = _cm(custom_page.get("margin_left")) or margin_left
        margin_right = _cm(custom_page.get("margin_right")) or margin_right

    for section in doc.sections:
        section.top_margin = margin_top
        section.bottom_margin = margin_bottom
        section.left_margin = margin_left
        section.right_margin = margin_right


def apply_format(
    paragraph,
    match_type: str,
    level: int | None,
    custom_settings: dict | None,
    flags: dict | None,
):
    """对单个段落逐属性覆盖格式。不复制其他段落的格式。"""
    flags = flags or {}

    # 1. 从硬编码 FORMAT_RULES 读取基准规则
    base_rule = get_rule(match_type, level)

    # 2. 合并自定义覆盖
    final_spec = dict(base_rule)
    if custom_settings:
        _apply_custom_overrides(final_spec, match_type, level, custom_settings)

    # 3. 段落级属性：逐属性读取原值后覆盖
    _apply_paragraph_properties(paragraph, final_spec)

    # 3.5 设置大纲级别（标题 → Word TOC 域可识别）
    if match_type == "heading" and level is not None:
        _set_outline_level(paragraph, level - 1)  # outlineLvl: 0=Level1, 1=Level2...
    elif match_type == "paper_title":
        _set_outline_level(paragraph, 0)

    # 4. 每个 run 独立处理，不批量复制
    for run in paragraph.runs:
        _apply_run_properties(run, final_spec)

    # 5. 西文字体
    if flags.get("latin_font", True):
        _apply_latin_to_runs(paragraph)


def apply_reference_format(paragraph, custom_settings: dict | None = None):
    """参考文献条目格式：硬编码规则 + 自定义覆盖 + 西文字体。"""
    base_rule = FORMAT_RULES["reference"]
    final_spec = dict(base_rule)
    if custom_settings:
        _apply_item_override(final_spec, custom_settings.get("reference"))

    _apply_paragraph_properties(paragraph, final_spec)
    for run in paragraph.runs:
        _apply_run_properties(run, final_spec)
    # 西文字体（含标点符号）：确保参考文献中英文及标点用 Times New Roman
    _apply_latin_to_runs(paragraph)


def apply_header_footer(doc, custom_settings: dict | None = None, flags: dict | None = None):
    """页眉页脚格式。"""
    base_rule = FORMAT_RULES["header_footer"]
    final_spec = dict(base_rule)
    if custom_settings:
        _apply_item_override(final_spec, custom_settings.get("header_footer"))

    for section in doc.sections:
        header = section.header
        if header.paragraphs:
            for para in header.paragraphs:
                _apply_paragraph_properties(para, final_spec)
                for run in para.runs:
                    _apply_run_properties(run, final_spec)


def apply_table_format(doc, custom_settings: dict | None = None, flags: dict | None = None):
    """统一表格格式：三线表边框 + 文字格式。"""
    base_rule = FORMAT_RULES["table_text"]
    final_spec = dict(base_rule)
    if custom_settings:
        _apply_item_override(final_spec, custom_settings.get("table_text"))
    flags = flags or {}

    for table in doc.tables:
        # 三线表边框
        _apply_three_line_table_borders(table)
        # 文字格式
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if not para.text.strip():
                        continue
                    for run in para.runs:
                        _apply_run_properties(run, final_spec)
                    if flags.get("latin_font", True):
                        _apply_latin_to_runs(para)


def should_skip_paragraph(paragraph) -> bool:
    """跳过表格内段落。图片段落不再跳过，在 service 层统一居中处理。"""
    parent_tag = paragraph._element.getparent().tag if paragraph._element.getparent() is not None else ""
    parent_local = parent_tag.split("}")[-1] if "}" in parent_tag else parent_tag
    if parent_local == "tc":
        return True
    return False


# ── Three-Line Table Borders ─────────────────────────

def _apply_three_line_table_borders(table):
    """对单个表格应用三线表边框（OOXML 层操作）。

    三线表标准：顶线和底线为粗线，表头下为细线，无线框。
    通过单元格级边框实现：首行单元格设顶边+底边，末行设底边。
    """
    tbl = table._tbl

    # 清除表级边框，改为 nil
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)

    # 移除旧表级边框
    old_borders = tblPr.find(qn("w:tblBorders"))
    if old_borders is not None:
        tblPr.remove(old_borders)

    # 设置表级无边框
    borders = OxmlElement("w:tblBorders")
    borders.append(_make_table_border("w:top", "single", 12))
    borders.append(_make_table_border("w:left", "nil", 0))
    borders.append(_make_table_border("w:bottom", "single", 12))
    borders.append(_make_table_border("w:right", "nil", 0))
    borders.append(_make_table_border("w:insideH", "nil", 0))
    borders.append(_make_table_border("w:insideV", "nil", 0))
    tblPr.append(borders)

    # 单元格级边框：首行顶+底，末行底，其余无边
    rows = table.rows
    for row_idx, row in enumerate(rows):
        is_header = row_idx == 0
        is_last = row_idx == len(rows) - 1
        for cell in row.cells:
            tc = cell._tc
            tcPr = tc.find(qn("w:tcPr"))
            if tcPr is None:
                tcPr = OxmlElement("w:tcPr")
                tc.insert(0, tcPr)
            # 移除旧单元格边框
            old_tc_borders = tcPr.find(qn("w:tcBorders"))
            if old_tc_borders is not None:
                tcPr.remove(old_tc_borders)
            tcBorders = OxmlElement("w:tcBorders")
            tcBorders.append(_make_table_border("w:top", "single" if is_header else "nil",
                                                 12 if is_header else 0))
            tcBorders.append(_make_table_border("w:left", "nil", 0))
            tcBorders.append(_make_table_border("w:bottom",
                                                 "single" if (is_header or is_last) else "nil",
                                                 12 if is_last else (6 if is_header else 0)))
            tcBorders.append(_make_table_border("w:right", "nil", 0))
            tcPr.append(tcBorders)

            # 单元格内容水平居左
            for para in cell.paragraphs:
                if para.text.strip():
                    from docx.enum.text import WD_ALIGN_PARAGRAPH
                    para.alignment = WD_ALIGN_PARAGRAPH.LEFT


def _make_table_border(name: str, val: str, sz: int):
    """创建表格边框 OOXML 元素。"""
    border = OxmlElement(name)
    border.set(qn("w:val"), val)
    border.set(qn("w:sz"), str(sz))
    border.set(qn("w:space"), "0")
    border.set(qn("w:color"), "000000" if val != "nil" else "auto")
    return border


# ── Equation Formatting ─────────────────────────────

def apply_equation_format(paragraph, eq_number: str, custom_settings: dict | None, flags: dict | None):
    """格式化公式段落：居中 + 编号右对齐（通过制表位实现）。

    公式段落使用两个制表位：
    - 居中制表位：让公式内容居中
    - 右对齐制表位：让编号靠右

    段落结构：<tab>公式内容<tab>(1-1)
    """
    base_rule = FORMAT_RULES["equation"]
    final_spec = dict(base_rule)
    if custom_settings:
        _apply_item_override(final_spec, custom_settings.get("equation"))
    flags = flags or {}

    # 段落属性：左对齐（实际通过制表位控制位置）
    from docx.enum.text import WD_ALIGN_PARAGRAPH as WD_ALIGN
    paragraph.alignment = WD_ALIGN.LEFT

    pf = paragraph.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = Cm(0)

    # 行距
    line_spacing = final_spec.get("line_spacing")
    if line_spacing is not None:
        rule = final_spec.get("line_spacing_rule")
        if rule == "EXACTLY":
            pf.line_spacing = Pt(line_spacing) if not isinstance(line_spacing, Length) else line_spacing

    # 设置制表位：居中 + 右对齐
    center_twips = final_spec.get("center_tab_twips", 4500)
    right_twips = final_spec.get("right_tab_twips", 9000)
    _set_custom_tab_stops(paragraph, [
        ("center", center_twips),
        ("right", right_twips),
    ])

    # Run 属性
    for run in paragraph.runs:
        run.font.size = final_spec.get("font_size", Pt(12))
        run.font.name = final_spec.get("font_name", FONT_LATIN)
        if final_spec.get("bold") is not None:
            run.bold = final_spec["bold"]

    # 如果没有制表符结构，重建：公式内容前加 tab，编号前加 tab
    full_text = paragraph.text
    if "\t" not in full_text and eq_number:
        # 保存原始 runs 的文字，重建段落
        original_text = full_text.replace(eq_number, "").strip()
        _rebuild_equation_paragraph(paragraph, original_text, eq_number, final_spec)


def _rebuild_equation_paragraph(paragraph, eq_text: str, number: str, spec: dict):
    """重建公式段落：<tab>公式<tab>编号"""
    # 清空
    for run in paragraph.runs:
        run._element.getparent().remove(run._element)

    # Tab1（定位到居中位置）
    run_tab1 = OxmlElement("w:r")
    tab1 = OxmlElement("w:tab")
    run_tab1.append(tab1)
    paragraph._element.append(run_tab1)

    # 公式内容
    if eq_text:
        run_eq = paragraph.add_run(eq_text)
        run_eq.font.size = spec.get("font_size", Pt(12))
        run_eq.font.name = spec.get("font_name", FONT_LATIN)

    # Tab2（定位到右对齐位置）
    run_tab2 = paragraph.add_run("\t")

    # 编号
    run_num = paragraph.add_run(number)
    run_num.font.size = spec.get("font_size", Pt(12))
    run_num.font.name = spec.get("font_name", FONT_LATIN)


def _set_custom_tab_stops(paragraph, tabs: list[tuple[str, int]]):
    """设置段落自定义制表位（清除默认制表位）。
    tabs: [(val, pos_twips), ...]  val ∈ {'left','center','right','decimal'}
    """
    pPr = paragraph._element.get_or_add_pPr()
    # 清除旧制表位
    old_tabs = pPr.find(qn("w:tabs"))
    if old_tabs is not None:
        pPr.remove(old_tabs)
    tabs_elem = OxmlElement("w:tabs")
    for val, pos in tabs:
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), val)
        tab.set(qn("w:pos"), str(pos))
        tabs_elem.append(tab)
    pPr.append(tabs_elem)


# ── Caption Renumbering ─────────────────────────────

def renumber_captions(doc, structure: dict):
    """按章节重新编号图题和表题。

    格式：图{chapter}.{index} / 表{chapter}.{index}
    每章内独立自增，附录用字母编号。
    """
    sections = structure.get("sections", [])
    chapter_map = _build_chapter_map(sections)

    current_chapter = 0
    fig_index = 0
    table_index = 0
    in_appendix = False
    appendix_letter = ""

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # 跟踪当前章节
        ch = _detect_chapter(text, chapter_map)
        if ch is not None:
            current_chapter = ch
            fig_index = 0
            table_index = 0
            in_appendix = False
            continue

        # 附录检测
        if _is_appendix_start(text):
            in_appendix = True
            fig_index = 0
            table_index = 0
            appendix_letter = _extract_appendix_letter(text)
            continue

        # 重编图题
        caption_type = _get_caption_type_for_renumber(text)
        if caption_type == "figure_caption":
            fig_index += 1
            prefix = appendix_letter if in_appendix else str(current_chapter or 1)
            new_number = f"图{prefix}.{fig_index}"
            _replace_caption_number(para, new_number)
        elif caption_type == "table_caption":
            table_index += 1
            prefix = appendix_letter if in_appendix else str(current_chapter or 1)
            new_number = f"表{prefix}.{table_index}"
            _replace_caption_number(para, new_number)


def _build_chapter_map(sections: list) -> dict:
    """构建章节标题 → 章节号映射。"""
    cmap = {}
    for sec in sections:
        numbering = sec.get("numbering", "")
        title = sec.get("title", "")
        full = f"{numbering}{title}".strip().replace(" ", "")
        # 提取章节号
        num_match = re.match(r"^(?:第)?(\d+)(?:章|节)?", numbering)
        if num_match:
            ch_num = int(num_match.group(1))
            cmap[full] = ch_num
    return cmap


def _detect_chapter(text: str, chapter_map: dict) -> int | None:
    """检测段落是否为章节标题，返回章节号。"""
    clean = text.strip().replace(" ", "")
    for full, ch_num in chapter_map.items():
        if clean == full or (len(full) >= 4 and clean.startswith(full[:4])):
            return ch_num
    return None


def _is_appendix_start(text: str) -> bool:
    """检测附录开始。"""
    return bool(re.match(r"^附\s*录\s*[A-Z]?", text.strip().replace(" ", "")))


def _extract_appendix_letter(text: str) -> str:
    """提取附录字母。"""
    m = re.search(r"附\s*录\s*([A-Z])", text.strip().replace(" ", ""))
    return m.group(1) if m else "A"


def _get_caption_type_for_renumber(text: str) -> str | None:
    """检测题注类型（简化版，用于重编号）。阈值与 matcher._get_caption_type 保持一致。"""
    stripped = text.strip()
    if len(stripped) > 50:
        return None
    if re.match(r"^(?:表|Table\.?)\s*\S+", stripped):
        return "table_caption"
    if re.match(r"^(?:图|Fig(?:ure)?\.?)\s*\S+", stripped):
        return "figure_caption"
    return None


def _replace_caption_number(paragraph, new_prefix: str):
    """替换题注的编号部分（仅修改第一个 run 的编号前缀，保留后续 run 格式）。

    例如 "图1.2 实验结果" → "图2.1 实验结果"，保留标题文字及其 run 格式。
    """
    if not paragraph.runs:
        return
    first_run = paragraph.runs[0]
    text = first_run.text
    # 只替换编号前缀（图/表 + 数字 + 可选的点号），保留后面的文字
    new_text = re.sub(
        r"^(?:图|Fig(?:ure)?\.?|表|Table\.?)\s*\S+\s*",
        new_prefix + " ",
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    first_run.text = new_text


# ── Reference Renumbering ───────────────────────────

def renumber_references(doc):
    """对参考文献进行连续编号 [1], [2], [3]...

    检测参考文献区域（从"参考文献"标题之后开始），
    对每条参考文献条目重新分配连续编号。
    """
    in_refs = False
    ref_index = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # 检测参考文献区域开始
        if not in_refs and _is_reference_heading(text):
            in_refs = True
            continue

        if not in_refs:
            continue

        # 检测是否离开参考文献区域
        if _is_out_of_references(text):
            in_refs = False
            continue

        # 判断是否为参考文献条目（而非空行/分隔符）
        if not _is_reference_entry(text):
            continue

        ref_index += 1
        new_prefix = f"[{ref_index}]"

        # 替换或添加编号
        _replace_reference_prefix(para, new_prefix)


def _is_reference_heading(text: str) -> bool:
    """检测参考文献标题。"""
    clean = text.strip().replace(" ", "")
    return clean in ("参考文献", "References") or clean.startswith("参考文献")


def _is_out_of_references(text: str) -> bool:
    """检测是否已离开参考文献区域（遇到致谢/附录等）。"""
    clean = text.strip().replace(" ", "")
    return clean.startswith("致谢") or clean.startswith("附录") or clean.startswith("作者简历")


def _is_reference_entry(text: str) -> bool:
    """判断是否为参考文献条目。"""
    # 有方括号编号
    if re.match(r"^\[\d+\]", text):
        return True
    # 有文献类型标识
    if re.search(r"\[[JMNDCPSROGZ][/]?[A-Za-z]*\]|\[EB/OL\]", text):
        return True
    # 英文作者+年份
    if re.match(r"^[A-Z][a-z]+[,]?\s+[A-Z]\.?\s*[,(]", text) and re.search(r"\d{4}", text):
        return True
    return False


def _replace_reference_prefix(paragraph, new_prefix: str):
    """替换参考文献条目的编号前缀。"""
    if not paragraph.runs:
        return

    # 拼接全文并去掉旧编号
    full_text = "".join(r.text for r in paragraph.runs)
    body = re.sub(r"^\[[\d,\s]*\]\s*", "", full_text.strip())

    # 直接重写所有 run: run[0] 放完整新文本，其余清空
    paragraph.runs[0].text = f"{new_prefix} {body}"
    for run in paragraph.runs[1:]:
        run.text = ""


# ── Footer Page Number ───────────────────────────────

def apply_footer_page_number(doc, custom_settings: dict | None = None):
    """在页脚添加/更新页码。支持自定义对齐方式。

    读取 custom_settings.footer_page_number:
      - enabled: bool — 是否启用页码
      - alignment: "LEFT" | "CENTER" | "RIGHT" — 页码对齐（默认 CENTER）
    """
    fp = custom_settings.get("footer_page_number") if custom_settings else None
    if not fp or not fp.get("enabled"):
        return

    alignment_str = fp.get("alignment", "CENTER").upper()
    from docx.enum.text import WD_ALIGN_PARAGRAPH as WD_ALIGN
    align_map = {"LEFT": WD_ALIGN.LEFT, "CENTER": WD_ALIGN.CENTER, "RIGHT": WD_ALIGN.RIGHT}
    align = align_map.get(alignment_str, WD_ALIGN.CENTER)

    for section in doc.sections:
        footer = section.footer
        if not footer.paragraphs:
            continue

        para = footer.paragraphs[0]
        # 清除旧内容
        for run in para.runs:
            run._element.getparent().remove(run._element)

        para.alignment = align

        # 插入 PAGE 域代码（Word 页码字段）
        run1 = para.add_run()
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        run1._element.append(fld_begin)

        run2 = para.add_run()
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        run2._element.append(instr)

        run3 = para.add_run()
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        run3._element.append(fld_sep)

        run4 = para.add_run("1")  # 占位数字
        run4.font.size = Pt(9)

        run5 = para.add_run()
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        run5._element.append(fld_end)


# ── internal helpers ──────────────────────────────

def _apply_custom_overrides(spec: dict, match_type: str, level: int | None, custom: dict):
    """将自定义设置覆盖到 spec 上。"""
    if match_type == "paper_title":
        _apply_item_override(spec, custom.get("title"))
    elif match_type == "heading" and level is not None:
        key = f"heading_{level}"
        _apply_item_override(spec, custom.get(key))
    elif match_type == "table_caption":
        _apply_item_override(spec, custom.get("table_caption"))
    elif match_type == "figure_caption":
        _apply_item_override(spec, custom.get("figure_caption"))
    elif match_type == "body":
        _apply_item_override(spec, custom.get("body"))
    elif match_type == "equation":
        _apply_item_override(spec, custom.get("equation"))
    elif match_type == "toc_title":
        _apply_item_override(spec, custom.get("toc_title"))
    elif match_type == "toc_entry":
        _apply_item_override(spec, custom.get("toc_entry"))


def _apply_item_override(spec: dict, item: dict | None):
    """单个格式项的覆盖。"""
    if not item or not item.get("enabled"):
        return
    if item.get("font_name"):
        spec["font_name"] = normalize_font_name(item["font_name"])
    if item.get("font_size_pt") is not None:
        spec["font_size"] = Pt(item["font_size_pt"])
    if item.get("bold") is not None:
        spec["bold"] = item["bold"]
    if item.get("alignment") is not None:
        spec["alignment"] = _parse_alignment(item["alignment"])
    if item.get("line_spacing") is not None:
        spec["line_spacing"] = item["line_spacing"]
    if item.get("line_spacing_rule") is not None:
        spec["line_spacing_rule"] = item["line_spacing_rule"]
    if item.get("first_line_indent") is not None:
        spec["first_line_indent"] = Cm(item["first_line_indent"])
    if item.get("space_before") is not None:
        spec["space_before"] = Pt(item["space_before"])
    if item.get("space_after") is not None:
        spec["space_after"] = Pt(item["space_after"])
    if item.get("character_spacing_pt") is not None:
        spec["character_spacing"] = item["character_spacing_pt"]
    if item.get("hanging_indent") is not None:
        spec["hanging_indent"] = Cm(item["hanging_indent"])


def _apply_paragraph_properties(paragraph, spec: dict):
    """逐属性覆盖段落格式。读取原值 → 按规则覆盖。"""
    pf = paragraph.paragraph_format

    # 对齐
    alignment = spec.get("alignment")
    if alignment is not None:
        paragraph.alignment = alignment

    # 行距
    # python-docx 的 pf.line_spacing setter: 传 float → 强制 MULTIPLE 模式;
    # 传 Pt(x) → 强制 EXACTLY 模式。因此 EXACTLY/AT_LEAST 必须用 Pt() 包装,
    # 且 AT_LEAST 需要 setter 之后再手动改回 AT_LEAST rule。
    line_spacing = spec.get("line_spacing")
    if line_spacing is not None:
        rule = spec.get("line_spacing_rule")
        if rule == "EXACTLY":
            pf.line_spacing = Pt(line_spacing) if not isinstance(line_spacing, Length) else line_spacing
        elif rule == "AT_LEAST":
            pf.line_spacing = Pt(line_spacing) if not isinstance(line_spacing, Length) else line_spacing
            pf.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
        else:
            pf.line_spacing = line_spacing

    # 段前段后
    space_before = spec.get("space_before")
    if space_before is not None:
        pf.space_before = space_before
    space_after = spec.get("space_after")
    if space_after is not None:
        pf.space_after = space_after

    # 首行缩进
    first_line_indent = spec.get("first_line_indent")
    if first_line_indent is not None:
        pf.first_line_indent = first_line_indent

    # 悬挂缩进（优先于首行缩进）：positive left_indent + negative first_line_indent
    hanging = spec.get("hanging_indent")
    if hanging is not None:
        pf.left_indent = hanging
        pf.first_line_indent = Cm(-float(hanging))


def _apply_run_properties(run, spec: dict):
    """逐属性覆盖 run 格式。每个 run 独立处理，不批量复制。"""
    font_name = spec.get("font_name")
    if font_name:
        set_east_asian_font(run, font_name)

    font_size = spec.get("font_size")
    if font_size is not None:
        run.font.size = font_size

    bold = spec.get("bold")
    if bold is not None:
        run.bold = bold

    # 显式设置颜色为黑色，不依赖默认值
    color = spec.get("color")
    if color is not None:
        run.font.color.rgb = color

    # 字符间距（w:spacing，单位 twips = pt × 20）
    char_spacing = spec.get("character_spacing")
    if char_spacing is not None:
        rPr = run._element.get_or_add_rPr()
        spacing_elem = rPr.find(qn("w:spacing"))
        if spacing_elem is None:
            spacing_elem = OxmlElement("w:spacing")
            rPr.append(spacing_elem)
        spacing_elem.set(qn("w:val"), str(int(char_spacing * 20)))

    # 确保下划线清除（学术论文标题可能有）
    run.underline = False

    # 兜底：清除被污染到 w:ascii / w:hAnsi 的中文字体名
    # （某些路径可能意外把东亚字体名写入西文槽位）
    if font_name:
        _normalized = normalize_font_name(font_name)
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is not None:
            _asc = rFonts.get(qn("w:ascii"))
            _ha = rFonts.get(qn("w:hAnsi"))
            # 如果 w:ascii 或 w:hAnsi 被设成了中文字体名 → 清除
            if _asc and _asc == _normalized:
                del rFonts.attrib[qn("w:ascii")]
            if _ha and _ha == _normalized:
                del rFonts.attrib[qn("w:hAnsi")]



def _apply_latin_to_runs(paragraph):
    """对所有 run 中的非中文字符（字母、数字、标点、符号）应用西文字体。

    之前只覆盖 [a-zA-Z0-9]，遗漏了英文标点如 .,;:()[] 等，
    导致参考文献条目中英文标点显示为中文字体而非 Times New Roman。
    """
    for run in paragraph.runs:
        # 只要 run 文本包含任何非中文字符，就设置西文字体
        # 覆盖：CJK 基本区 + CJK Extension A + CJK 符号 + 全角半角
        if re.search(r"[^一-鿿㐀-䶿　-〿＀-￯]", run.text):
            set_latin_font(run, defaults.FONT_LATIN)


def _parse_alignment(value: str):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    mapping = {
        "LEFT": WD_ALIGN_PARAGRAPH.LEFT,
        "CENTER": WD_ALIGN_PARAGRAPH.CENTER,
        "RIGHT": WD_ALIGN_PARAGRAPH.RIGHT,
        "JUSTIFY": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "DISTRIBUTE": WD_ALIGN_PARAGRAPH.DISTRIBUTE,
    }
    return mapping.get(value.upper() if value else "", WD_ALIGN_PARAGRAPH.LEFT)


def _cm(value) -> Cm | None:
    if value is None:
        return None
    try:
        return Cm(float(value))
    except (TypeError, ValueError):
        return None


def _set_outline_level(paragraph, level: int):
    """设置段落的大纲级别（w:outlineLvl），供 Word TOC 域识别。
    level 0 = 一级标题，1 = 二级标题，以此类推。
    """
    pPr = paragraph._element.get_or_add_pPr()
    existing = pPr.find(qn("w:outlineLvl"))
    if existing is not None:
        pPr.remove(existing)
    ol = OxmlElement("w:outlineLvl")
    ol.set(qn("w:val"), str(level))
    pPr.append(ol)


def enable_auto_update_fields(doc):
    """在文档设置中启用自动更新域（w:updateFields），
    使 Word 打开时自动刷新 TOC 域代码，无需手动 F9。
    """
    settings = doc.settings
    existing = settings.element.find(qn("w:updateFields"))
    if existing is None:
        uf = OxmlElement("w:updateFields")
        uf.set(qn("w:val"), "true")
        settings.element.append(uf)
