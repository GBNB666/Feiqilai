"""预览服务 — 结构化内容提取"""
import json
from docx import Document
from app.modules.format_engine.matcher import match_paragraph, is_table_paragraph, is_image_paragraph


class PreviewService:
    @staticmethod
    def extract(file_path: str, structure: dict) -> list[dict]:
        """提取格式化后的结构化预览数据"""
        doc = Document(file_path)
        matched_sections = set()
        result = []
        current_section = None
        in_toc = False

        for para in doc.paragraphs:
            if is_table_paragraph(para):
                continue
            text = para.text.strip()
            if not text:
                continue

            if "目录" in text and not matched_sections:
                in_toc = True

            match_type, level = match_paragraph(text, structure, matched_sections)
            is_image = is_image_paragraph(para)

            if match_type in ("paper_title", "subtitle", "special_heading", "heading") or (
                level is not None and not current_section
            ):
                in_toc = False
                if current_section:
                    result.append(current_section)
                current_section = {
                    "level": level or 1,
                    "title": text[:80],
                    "content": [],
                    "markers": [],
                    "is_toc": in_toc,
                }
            elif current_section is not None and not in_toc:
                if is_image:
                    current_section["markers"].append({
                        "type": "image",
                        "index": len(current_section["markers"]) + 1,
                        "description": text[:60],
                    })
                elif is_table_paragraph(para):
                    current_section["markers"].append({
                        "type": "table",
                        "index": len(current_section["markers"]) + 1,
                        "description": text[:60],
                    })
                else:
                    current_section["content"].append(text)

        if current_section:
            result.append(current_section)
        return result
