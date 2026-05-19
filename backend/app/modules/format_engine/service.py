"""排版引擎 — 编排整体排版流程"""
import json
from pathlib import Path
from docx import Document
from app.config import settings
from app.modules.format_engine.matcher import (
    match_paragraph,
    is_table_paragraph,
    is_image_paragraph,
    is_caption_text,
)
from app.modules.format_engine.applier import (
    apply_page_settings,
    apply_format,
    apply_header_footer,
    reset_run_color,
)
from app.modules.format_engine.toc import remove_old_toc, generate_toc


class FormatEngine:
    @staticmethod
    def execute(
        input_path: str,
        output_path: str,
        structure: dict,
        custom_settings: dict | None = None,
        enabled_flags: dict | None = None,
    ) -> None:
        """执行完整排版流程"""
        doc = Document(input_path)

        # 1. 移除旧目录
        remove_old_toc(doc)

        # 2. 应用页面设置
        apply_page_settings(doc, custom_settings, enabled_flags)

        # 3. 段落匹配和格式应用
        matched_sections = set()
        in_reference = False
        paper_title = structure.get("title", "")

        for para in doc.paragraphs:
            # 跳过表格内段落和图片段落
            if is_table_paragraph(para) or is_image_paragraph(para):
                continue

            text = para.text.strip()
            if not text:
                continue

            # 检测参考文献区
            if "参考文献" in text and "references_section" not in matched_sections:
                in_reference = True
                matched_sections.add("references_section")

            # 重置颜色
            reset_run_color(para)

            # 匹配
            match_type, level = match_paragraph(text, structure, matched_sections)

            # 应用格式
            apply_format(
                para,
                match_type,
                level,
                custom_settings,
                enabled_flags,
                in_reference_section=in_reference,
            )

        # 4. 应用页眉页脚
        apply_header_footer(doc, paper_title, custom_settings, enabled_flags)

        # 5. 生成目录
        merged_toc = True
        if custom_settings and "toc_enabled" in custom_settings:
            merged_toc = custom_settings["toc_enabled"]
        if merged_toc:
            generate_toc(doc, structure, custom_settings, enabled_flags)

        # 6. 保存
        # PDF 输入 → 强制输出 .docx
        output = Path(output_path)
        if output.suffix.lower() == ".pdf":
            output = output.with_suffix(".docx")
        doc.save(str(output))

    @staticmethod
    def preview_formatted(input_path: str, structure: dict) -> list[dict]:
        """提取格式化后的结构化预览数据"""
        doc = Document(input_path)
        matched_sections = set()
        sections = structure.get("sections", [])
        result = []
        current_section = None
        in_toc = False

        for para in doc.paragraphs:
            if is_table_paragraph(para) or is_image_paragraph(para):
                continue
            text = para.text.strip()
            if not text:
                continue

            # TOC 检测
            if "目录" in text and not matched_sections:
                in_toc = True

            match_type, level = match_paragraph(text, structure, matched_sections)

            if match_type in ("paper_title", "subtitle", "special_heading", "heading"):
                in_toc = False
                if current_section:
                    result.append(current_section)
                current_section = {
                    "level": level or 0,
                    "title": text[:50],
                    "content": [],
                    "markers": [],
                }
            elif current_section is not None and not in_toc:
                # 检测图表标记
                if is_image_paragraph(para):
                    current_section["markers"].append({"type": "image", "text": text[:30]})
                else:
                    current_section["content"].append(text)

        if current_section:
            result.append(current_section)
        return result
