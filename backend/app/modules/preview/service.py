import json
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
from app.modules.format_engine.matcher import match_paragraph, is_in_reference_zone, is_equation_paragraph
from app.shared.schemas import ContentMarker, SectionPreview


def _extract_font_info(para) -> dict:
    """从段落第一个 run 提取字体格式信息。"""
    info = {
        "font_name": None,
        "font_size_pt": None,
        "bold": None,
        "alignment": None,
    }
    if para.runs:
        run = para.runs[0]
        if run.font.name:
            info["font_name"] = run.font.name
        if run.font.size:
            info["font_size_pt"] = round(run.font.size.pt, 1)
        if run.bold is not None:
            info["bold"] = run.bold
    # 对齐
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    align_map = {
        WD_ALIGN_PARAGRAPH.LEFT: "LEFT",
        WD_ALIGN_PARAGRAPH.CENTER: "CENTER",
        WD_ALIGN_PARAGRAPH.RIGHT: "RIGHT",
        WD_ALIGN_PARAGRAPH.JUSTIFY: "JUSTIFY",
    }
    info["alignment"] = align_map.get(para.alignment)
    return info


class PreviewService:
    @staticmethod
    def extract(file_path: str, structure: dict) -> list[dict]:
        """提取结构化预览内容（含字体格式信息）。
        无论文档有无目录/章节，始终返回可展示的内容。
        """
        doc = Document(file_path)
        matched_sections: set = set()
        sections = structure.get("sections", [])

        # Build section key → index map
        bucket_map: dict[str, int] = {}
        for i, sec in enumerate(sections):
            num = sec.get("numbering", "")
            title = sec.get("title", "")
            key = f"{num}{title}".strip().replace(" ", "")
            bucket_map[key] = i

        # Init buckets from AI sections
        buckets: list[dict] = []
        for sec in sections:
            num = sec.get("numbering", "")
            title = sec.get("title", "")
            buckets.append({
                "level": sec.get("level", 0),
                "title": f"{num}{title}",
                "content": [],
                "markers": [],
                "is_toc": False,
                "font_info": None,
                "body_sample": None,
            })

        # Always prepend a preamble / catch-all bucket so content before
        # the first heading (or all content when no heading matches) is never lost.
        preamble_title = "前言" if sections else "全文内容"
        buckets.insert(0, {
            "level": 0,
            "title": preamble_title,
            "content": [],
            "markers": [],
            "is_toc": False,
            "font_info": None,
            "body_sample": None,
        })

        # Shift bucket_map indices by +1 to account for preamble
        for key in list(bucket_map.keys()):
            bucket_map[key] += 1

        current_bucket = 0
        in_references = False
        in_toc_zone = False

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check table cell parent
            parent_tag = para._element.getparent().tag if para._element.getparent() is not None else ""
            parent_local = parent_tag.split("}")[-1] if "}" in parent_tag else parent_tag
            if parent_local == "tc":
                if current_bucket >= 0 and current_bucket < len(buckets):
                    buckets[current_bucket]["markers"].append(
                        ContentMarker(type="table", label=text[:30]).model_dump()
                    )
                continue

            # Check for images
            has_image = False
            for run in para.runs:
                drawings = run._element.findall(qn("w:drawing"))
                blips = run._element.findall(".//" + qn("a:blip"))
                if drawings or blips:
                    has_image = True
                    break
            if has_image:
                if current_bucket >= 0 and current_bucket < len(buckets):
                    buckets[current_bucket]["markers"].append(
                        ContentMarker(type="image", label="[图片]").model_dump()
                    )
                continue

            # TOC zone detection — only skip the "目录" title line itself, not the entries
            if "目录" in text.replace(" ", "") and len(text.replace(" ", "")) <= 6 and not in_toc_zone:
                in_toc_zone = True
                continue

            in_references = is_in_reference_zone(text, in_references)

            # 公式段落标记
            if is_equation_paragraph(text) and not in_references:
                if current_bucket >= 0 and current_bucket < len(buckets):
                    buckets[current_bucket]["markers"].append(
                        ContentMarker(type="equation", label=text[:40]).model_dump()
                    )
                continue

            # 记录匹配前的状态，以便精确定位本次命中了哪个 section
            prev_matched = set(matched_sections)
            match_type, level = match_paragraph(text, structure, matched_sections)

            if match_type == "heading" and level is not None and sections:
                # 找到本次新增的 section key → 切换到对应 bucket
                new_keys = matched_sections - prev_matched
                for key in new_keys:
                    if key in bucket_map:
                        current_bucket = bucket_map[key]
                        # 提取标题字体信息
                        buckets[current_bucket]["font_info"] = _extract_font_info(para)
                        break
                continue

            if match_type == "paper_title":
                # 提取论文标题字体信息（给第一个 bucket）
                if buckets and buckets[0]["font_info"] is None:
                    buckets[0]["font_info"] = _extract_font_info(para)
                continue

            if current_bucket >= 0 and current_bucket < len(buckets):
                if match_type in ("body", "table_caption", "figure_caption"):
                    buckets[current_bucket]["content"].append(text)
                    # 保存第一段正文样本及字体信息（最多 60 字）
                    if buckets[current_bucket]["body_sample"] is None and match_type == "body":
                        buckets[current_bucket]["body_sample"] = {
                            "text": text[:60],
                            "font_info": _extract_font_info(para),
                        }
                elif match_type == "unknown" and not sections:
                    # 无章节划分时，所有正文都收集
                    buckets[current_bucket]["content"].append(text)
                    if buckets[current_bucket]["body_sample"] is None:
                        buckets[current_bucket]["body_sample"] = {
                            "text": text[:60],
                            "font_info": _extract_font_info(para),
                        }

        # 过滤掉完全空的 buckets（无标题无内容的）
        buckets = [b for b in buckets if b["title"] or b["content"] or b["markers"]]
        if not buckets:
            buckets.append({
                "level": 0,
                "title": "文档内容",
                "content": ["文档已排版完成，请下载查看完整效果。"],
                "markers": [],
                "is_toc": False,
                "font_info": None,
                "body_sample": None,
            })

        return buckets
