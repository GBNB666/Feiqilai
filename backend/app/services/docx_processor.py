from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.services.format_standards import (
    apply_page_settings as _std_page,
    apply_heading_format,
    apply_body_format,
    apply_caption_format,
    is_caption_paragraph,
    HEADING_SPECS,
)

ALIGN_MAP = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def extract_text(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())
    return "\n\n".join(paragraphs)


def _ensure_heading_style(doc: Document, level: int, custom=None):
    name = f"Heading {level}"
    try:
        return doc.styles[name]
    except KeyError:
        style = doc.styles.add_style(name, 1)
        spec = HEADING_SPECS[level]
        style.font.size = Pt(custom.font_size) if custom and custom.font_size else spec["size"]
        style.font.bold = custom.bold if custom else spec["bold"]
        return style


def _apply_header_footer_font(section, header_custom, footer_custom, default_spec: dict):
    """Apply font to header and footer paragraphs."""
    for target, cfg in [(section.header, header_custom), (section.footer, footer_custom)]:
        if target is None:
            continue
        for para in target.paragraphs:
            for run in para.runs:
                run.font.size = Pt(cfg.font_size) if cfg and cfg.font_size else default_spec.get("size", Pt(9))
                run.font.bold = cfg.bold if cfg else False
                fname = cfg.font_name if cfg and cfg.font_name else default_spec.get("font_name", "宋体")
                run.font.name = fname
                _set_run_east_font(run, fname)
            pf = para.paragraph_format
            if cfg and cfg.alignment:
                pf.alignment = ALIGN_MAP.get(cfg.alignment, WD_ALIGN_PARAGRAPH.CENTER)


def _apply_custom_para(para, custom, default_spec: dict, enabled=None):
    """Apply custom or default formatting to a paragraph, respecting enabled flags."""
    pf = para.paragraph_format
    if enabled is None or enabled.alignment:
        pf.alignment = ALIGN_MAP.get(custom.alignment, default_spec.get("align", WD_ALIGN_PARAGRAPH.LEFT))
    if enabled is None or enabled.line_spacing:
        pf.line_spacing = custom.line_spacing or default_spec.get("line_spacing", 1.5)
    if enabled is None or enabled.space_before:
        pf.space_before = Pt(custom.space_before) if custom.space_before else default_spec.get("space_before", Pt(0))
    if enabled is None or enabled.space_after:
        pf.space_after = Pt(custom.space_after) if custom.space_after else default_spec.get("space_after", Pt(0))
    if enabled is None or enabled.first_line_indent:
        if custom.first_line_indent:
            pf.first_line_indent = Pt(custom.first_line_indent)
        elif default_spec.get("first_line_indent"):
            pf.first_line_indent = default_spec["first_line_indent"]
        else:
            pf.first_line_indent = None

    for run in para.runs:
        if enabled is None or enabled.font_size:
            run.font.size = Pt(custom.font_size) if custom.font_size else default_spec.get("size", Pt(12))
        if enabled is None or enabled.bold:
            run.font.bold = custom.bold if hasattr(custom, 'bold') and custom.bold is not None else default_spec.get("bold", False)
        if enabled is None or enabled.font_name:
            fname = custom.font_name or default_spec.get("font_name", "宋体")
            run.font.name = fname
            _set_run_east_font(run, fname)


def _set_run_east_font(run, font_name: str):
    try:
        from lxml import etree
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        if rFonts is None:
            rFonts = etree.SubElement(rPr, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
        rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", font_name)
    except Exception:
        pass


def _text_matches_title(para_text: str, title: str) -> bool:
    """Check if paragraph text matches a section title (heading detection)."""
    if not title or not para_text:
        return False
    t = para_text.replace(' ', '').replace('　', '')
    tt = title.replace(' ', '').replace('　', '')
    if not t or not tt:
        return False
    # Exact match
    if t == tt:
        return True
    # Paragraph starts with title (e.g. "1 引言" heading followed by body)
    if t.startswith(tt):
        return True
    # Title inside paragraph - only if paragraph is reasonably short (heading-like)
    if tt in t and len(t) < 100 and t.index(tt) < 30:
        return True
    return False


def _detect_toc(doc) -> dict:
    """Detect if the document has a TOC by searching for '目录' keyword in first 20 paragraphs."""
    for i, para in enumerate(doc.paragraphs):
        if i > 20:
            break
        text = para.text.strip().replace(" ", "").replace("　", "")
        if "目录" in text:
            end = i + 1
            for j in range(i + 1, min(len(doc.paragraphs), i + 50)):
                p = doc.paragraphs[j]
                if p.style and "Heading" in (p.style.name or ""):
                    end = j
                    break
            return {"has_toc": True, "start_idx": i, "end_idx": end}
    return {"has_toc": False, "start_idx": -1, "end_idx": -1}


def _apply_toc_format(run, para, cfg, enabled):
    """Apply TOC formatting to a run and paragraph."""
    if enabled is None or enabled.font_name:
        run.font.name = cfg.font_name
        _set_run_east_font(run, cfg.font_name)
    if enabled is None or enabled.font_size:
        run.font.size = Pt(cfg.font_size)
    if enabled is None or enabled.bold:
        run.font.bold = cfg.bold
    if enabled is None or enabled.alignment:
        para.paragraph_format.alignment = ALIGN_MAP.get(cfg.alignment, WD_ALIGN_PARAGRAPH.LEFT)
    if enabled is None or enabled.line_spacing:
        para.paragraph_format.line_spacing = cfg.line_spacing or 1.5


def _generate_toc(doc, structure, custom_settings, enabled_settings):
    """Generate TOC at the beginning of the document, before the first heading."""
    if not custom_settings or not custom_settings.toc_enabled:
        return

    title_cfg = custom_settings.toc_title
    entry_cfg = custom_settings.toc_entry
    title_en = enabled_settings.toc_title if enabled_settings else None
    entry_en = enabled_settings.toc_entry if enabled_settings else None

    # Find insertion point: first heading-style paragraph
    insert_before = None
    for para in doc.paragraphs:
        if para.style and "Heading" in (para.style.name or ""):
            insert_before = para
            break

    if insert_before is None:
        # No headings found, insert at beginning
        if doc.paragraphs:
            insert_before = doc.paragraphs[0]

    # Build TOC entries from structure
    entries = []
    for s in structure.get("sections", []):
        level = s.get("level", 1)
        title = s.get("title", "")
        if not title:
            continue
        if level > 2 and not custom_settings.toc_include_h3:
            continue
        entries.append((level, title))

    if not entries:
        return

    # Helper to insert a new paragraph before insert_before
    def _insert_para(text):
        if insert_before:
            p = insert_before.insert_paragraph_before("")
        else:
            p = doc.add_paragraph("")
        if text:
            p.clear()
            run = p.add_run(text)
            return p, run
        return p, None

    # Insert TOC title
    tp, tr = _insert_para("")
    tr = tp.add_run("目  录") if tr is None else tr
    if tr.text == "":
        tr.text = "目  录"
    _apply_toc_format(tr, tp, title_cfg, title_en)

    # Insert entries
    for level, title in entries:
        indent = "    " * (level - 1)
        line = f"{indent}{title}"
        if custom_settings.toc_show_page_numbers:
            line += "  [页码]"
        ep, er = _insert_para("")
        er = ep.add_run(line) if er is None else er
        if er.text == "":
            er.text = line
        _apply_toc_format(er, ep, entry_cfg, entry_en)

    # Blank line after TOC
    _insert_para("")


def apply_formatting(input_path: str, output_path: str, structure: dict, custom_settings=None, enabled_settings=None) -> str:
    doc = Document(input_path)

    # TOC detection
    toc_info = _detect_toc(doc)
    structure["has_toc"] = toc_info["has_toc"]

    # Remove existing TOC paragraphs if we're going to regenerate
    toc_removed = False
    if toc_info["has_toc"] and custom_settings and custom_settings.toc_enabled:
        # Remove old TOC paragraphs (from end to start to preserve indices)
        for i in range(toc_info["end_idx"] - 1, toc_info["start_idx"] - 1, -1):
            if i < len(doc.paragraphs):
                p = doc.paragraphs[i]._element
                p.getparent().remove(p)
        toc_removed = True

    # Generate new TOC
    if custom_settings and custom_settings.toc_enabled:
        _generate_toc(doc, structure, custom_settings, enabled_settings)

    # Build skip set for original TOC paragraphs (only if we didn't remove them)
    toc_skip = set()
    if toc_info["has_toc"] and not toc_removed and not (custom_settings and custom_settings.toc_enabled):
        toc_skip = set(range(toc_info["start_idx"], toc_info["end_idx"]))

    # Apply page settings (custom or standard), checking enabled flags
    if custom_settings:
        en = enabled_settings
        for section in doc.sections:
            if en is None or en.page_margin_top:
                section.top_margin = Cm(custom_settings.page_margin_top)
            if en is None or en.page_margin_bottom:
                section.bottom_margin = Cm(custom_settings.page_margin_bottom)
            if en is None or en.page_margin_left:
                section.left_margin = Cm(custom_settings.page_margin_left)
            if en is None or en.page_margin_right:
                section.right_margin = Cm(custom_settings.page_margin_right)
            if en is None or en.header_distance:
                section.header_distance = Cm(custom_settings.header_distance)
            if en is None or en.footer_distance:
                section.footer_distance = Cm(custom_settings.footer_distance)
            _apply_header_footer_font(section, custom_settings.header, custom_settings.footer, {"font_name": "宋体", "size": Pt(9)})
    else:
        _std_page(doc)

    h_styles = {
        1: _ensure_heading_style(doc, 1, custom_settings.h1 if custom_settings else None),
        2: _ensure_heading_style(doc, 2, custom_settings.h2 if custom_settings else None),
        3: _ensure_heading_style(doc, 3, custom_settings.h3 if custom_settings else None),
    }

    sections = structure.get("sections", [])
    custom_h = {1: custom_settings.h1, 2: custom_settings.h2, 3: custom_settings.h3} if custom_settings else {}
    custom_h_en = {1: enabled_settings.h1, 2: enabled_settings.h2, 3: enabled_settings.h3} if enabled_settings else {}
    custom_body = custom_settings.body if custom_settings else None
    custom_body_en = enabled_settings.body if enabled_settings else None
    custom_cap = custom_settings.caption if custom_settings else None
    custom_cap_en = enabled_settings.caption if enabled_settings else None

    # Build lookup structures for heading matching
    title_sections = [(s.get('title', ''), s) for s in sections if s.get('title')]
    marker_sections = [(s.get('start_marker', ''), s) for s in sections if s.get('start_marker')]
    matched_sections = set()  # sections already matched — prevent duplicate matching

    # Check for paper title (from structure, not in sections list)
    paper_title = structure.get('title', '')

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        matched_level = None

        # Strategy 0: Match paper title (first heading-like paragraph matching structure.title)
        if paper_title and _text_matches_title(text, paper_title):
            matched_level = 1
            matched_sections.add(paper_title)

        # Strategy 1: Match by section TITLE (most reliable — title is heading text)
        if matched_level is None:
            for title, section in title_sections:
                if title not in matched_sections and _text_matches_title(text, title):
                    matched_level = section.get("level", 1)
                    matched_sections.add(title)
                    break

        # Strategy 2: Fallback to start_marker (only for sections not yet matched by title)
        if matched_level is None:
            for marker, section in marker_sections:
                title = section.get('title', '')
                if title in matched_sections:
                    continue  # already found this section's heading, don't re-match
                if marker and len(marker) >= 6 and marker in text:
                    matched_level = section.get("level", 1)
                    matched_sections.add(title)
                    break

        if matched_level:
            ch = custom_h.get(matched_level)
            ch_en = custom_h_en.get(matched_level)
            if ch and (ch.font_name or ch.font_size):
                _apply_custom_para(para, ch, HEADING_SPECS.get(matched_level, HEADING_SPECS[1]), ch_en)
            else:
                apply_heading_format(para, matched_level)
            para.style = h_styles[matched_level]
            # Clear first-line indent for all headings
            para.paragraph_format.first_line_indent = None
        elif is_caption_paragraph(text):
            if custom_cap:
                _apply_custom_para(para, custom_cap, {"align": WD_ALIGN_PARAGRAPH.CENTER, "line_spacing": 1.5, "size": Pt(10.5), "font_name": "宋体"}, custom_cap_en)
            else:
                apply_caption_format(para)
        else:
            if custom_body:
                _apply_custom_para(para, custom_body, {"align": WD_ALIGN_PARAGRAPH.JUSTIFY, "line_spacing": 1.5, "first_line_indent": Pt(24), "size": Pt(12), "font_name": "宋体"}, custom_body_en)
            else:
                apply_body_format(para)

    doc.save(output_path)
    return output_path


def modify_section_content(file_path: str, section_index: int, new_content: str) -> None:
    """Replace the body text of a specific section in the output document."""
    doc = Document(file_path)
    body_idx = 0
    in_target = False
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # Heuristic: first significant paragraph after section break is section body
        if para.style and "Heading" in (para.style.name or ""):
            body_idx += 1
            in_target = (body_idx - 1) == section_index
            continue
        if in_target and para.text.strip():
            # Replace this paragraph with new content, keep remaining
            for run in para.runs:
                run.text = ""
            para.runs[0].text = new_content if para.runs else None
            if not para.runs:
                para.add_run(new_content)
            break
    doc.save(file_path)


def _get_image_dims(el, nsmap):
    """Extract image dimensions from a drawing element, returns (width_px, height_px) or (None, None)."""
    try:
        for inline in el.findall('.//wp:inline', nsmap) or el.findall('.//wp:anchor', nsmap):
            extent = inline.find('.//wp:extent', nsmap)
            if extent is not None:
                cx = int(extent.get('cx', 0))
                cy = int(extent.get('cy', 0))
                # EMU to pixels at 96 DPI
                return (round(cx / 9525), round(cy / 9525))
    except Exception:
        pass
    return (None, None)


def extract_formatted_content(file_path: str, structure: dict) -> list[dict]:
    """Extract formatted content as structured sections for preview, with markers and TOC."""
    doc = Document(file_path)
    sections = structure.get("sections", [])
    result_sections = []
    current_section = None
    current_body = []
    current_markers = []
    marker_idx = {"table": 0, "image": 0}

    nsmap = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    }

    # Detect TOC paragraphs for skipping in main content
    toc_info = _detect_toc(doc)
    toc_skip = set()
    toc_entries = []
    if toc_info["has_toc"]:
        toc_skip = set(range(toc_info["start_idx"], toc_info["end_idx"]))
        for i in range(toc_info["start_idx"], toc_info["end_idx"]):
            if i < len(doc.paragraphs):
                t = doc.paragraphs[i].text.strip()
                if t and "目录" not in t.replace(" ", "").replace("　", ""):
                    toc_entries.append(t)

    # Build para -> section map: title match first, marker fallback (one match per section)
    para_section_map = {}
    matched_set = set()
    for s in sections:
        title = s.get("title", "")
        marker = s.get("start_marker", "")
        # Title match first
        for i, para in enumerate(doc.paragraphs):
            if title and title not in matched_set and _text_matches_title(para.text.strip(), title):
                para_section_map[i] = s
                matched_set.add(title)
                break
        # Marker fallback (only if this section not already matched)
        if title not in matched_set:
            for i, para in enumerate(doc.paragraphs):
                if marker and len(marker) >= 6 and marker in para.text:
                    para_section_map[i] = s
                    matched_set.add(title)
                    break

    for i, para in enumerate(doc.paragraphs):
        # Skip TOC paragraphs
        if i in toc_skip:
            continue

        # Skip paragraphs inside tables
        parent_tag = para._element.getparent().tag.split('}')[-1] if para._element.getparent() is not None else ''
        if parent_tag == 'tc':
            continue

        text = para.text.strip()

        # Check for images in this paragraph
        has_image = len(para._element.findall('.//wp:inline', nsmap)) > 0 or \
                    len(para._element.findall('.//wp:anchor', nsmap)) > 0
        if has_image:
            if current_section is not None:
                idx = marker_idx["image"]
                marker_idx["image"] += 1
                w, h = _get_image_dims(para._element, nsmap)
                current_markers.append({
                    "type": "image", "index": idx,
                    "description": f"图片：宽{w}px×高{h}px" if w else "图片（嵌入）",
                    "rows": None, "cols": None,
                    "width_px": w, "height_px": h,
                })
            continue

        if not text:
            continue

        if i in para_section_map:
            if current_section is not None:
                current_section["content"] = "\n".join(current_body)
                current_section["markers"] = current_markers
                result_sections.append(current_section)
            current_section = {
                "level": para_section_map[i]["level"],
                "title": para_section_map[i]["title"],
                "content": "",
            }
            current_body = []
            current_markers = []
            marker_idx = {"table": 0, "image": 0}
        else:
            current_body.append(text)

    # Detect tables and assign to last section
    if doc.tables:
        for table in doc.tables:
            rows = len(table.rows)
            cols = max(len(row.cells) for row in table.rows) if table.rows else 0
            idx = marker_idx["table"]
            marker_idx["table"] += 1
            marker = {
                "type": "table", "index": idx,
                "description": f"表格：{rows}行×{cols}列",
                "rows": rows, "cols": cols,
                "width_px": None, "height_px": None,
            }
            if current_section is not None:
                current_markers.append(marker)

    if current_section is not None:
        current_section["content"] = "\n".join(current_body)
        current_section["markers"] = current_markers
        result_sections.append(current_section)

    if not result_sections:
        all_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip() and doc.paragraphs.index(p) not in toc_skip)
        result_sections = [{"level": 0, "title": structure.get("title", "正文"), "content": all_text, "markers": []}]

    # Prepend TOC section if detected
    if toc_info["has_toc"] and toc_entries:
        toc_section = {
            "level": -1,
            "title": "目录",
            "content": "\n".join(toc_entries),
            "markers": [],
        }
        result_sections.insert(0, toc_section)

    return result_sections
