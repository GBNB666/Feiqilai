from PyPDF2 import PdfReader


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages.append(text.strip())
    return "\n\n".join(pages)


def apply_formatting(input_path: str, output_path: str, structure: dict) -> str:
    """PDF formatting: generate a formatted DOCX from the PDF text content."""
    from docx import Document
    from app.services.format_standards import (
        apply_page_settings, apply_heading_format,
        apply_body_format, apply_caption_format, is_caption_paragraph,
        HEADING_SPECS,
    )

    reader = PdfReader(input_path)
    paragraphs = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    paragraphs.append(line)

    doc = Document()
    apply_page_settings(doc)

    h_styles = {}
    for lv in [1, 2, 3]:
        try:
            h_styles[lv] = doc.styles[f"Heading {lv}"]
        except KeyError:
            style = doc.styles.add_style(f"Heading {lv}", 1)
            spec = HEADING_SPECS[lv]
            style.font.size = spec["size"]
            style.font.bold = spec["bold"]
            h_styles[lv] = style

    sections = structure.get("sections", [])

    for text in paragraphs:
        para = doc.add_paragraph(text)

        matched_level = None
        for section in sections:
            marker = section.get("start_marker", "")
            if marker and marker in text:
                matched_level = section.get("level", 1)
                break

        if matched_level:
            apply_heading_format(para, matched_level)
            para.style = h_styles[matched_level]
        elif is_caption_paragraph(text):
            apply_caption_format(para)
        else:
            apply_body_format(para)

    doc.save(output_path)
    return output_path
