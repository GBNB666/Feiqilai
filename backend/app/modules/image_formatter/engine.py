"""
论文图片自动排版模块 (Image Auto-Formatter)

功能:
  1. 自动识别文档中所有图片，统一宽度并按比例缩放
  2. 自动生成图片编号（"图1"、"图2"……），宋体五号加粗
  3. 图注文字统一为宋体五号居中
  4. 图片与正文间距约 0.5 行
  5. 确保图片不跨页断档（keepNext + keepLines）
  6. 返回处理后的文件路径和图片数量

用法:
  >>> from app.modules.image_formatter.engine import auto_format_images
  >>> path, count = auto_format_images("paper.docx", width_ratio=0.7)
  >>> print(f"处理完成: {path}, 共 {count} 张图片")
"""

import os
import re
import copy
from typing import Tuple, Optional, List, Dict

from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ── 常量 ──────────────────────────────────────────────

FONT_LABEL = "宋体"        # 图片编号字体
FONT_CAPTION = "宋体"      # 图注字体
SIZE_LABEL = Pt(10.5)      # 五号
SIZE_CAPTION = Pt(10.5)    # 五号


# ── 主函数 ────────────────────────────────────────────

def auto_format_images(
    docx_path: str,
    output_path: Optional[str] = None,
    width_ratio: float = 0.7,
    number_format: str = "图{num}",
    label_position: str = "above",
    image_ratios: Optional[Dict[int, float]] = None,
    alignment: Optional[str] = None,
) -> Tuple[str, int]:
    """自动排版论文中的图片。

    Args:
        docx_path:       输入 DOCX 文件路径
        output_path:     输出文件路径，默认在原名后加 "_images_formatted"
        width_ratio:     默认图片宽度比例 (0.1~1.0)
        number_format:   编号格式，必须含 {num} 占位符
        label_position:  编号位置: "above" 或 "below"
        image_ratios:    每张图片的独立比例 {image_index: ratio}，优先于 width_ratio

    Returns:
        (output_path, image_count)
    """
    # ── 参数校验 ──
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"文件不存在: {docx_path}")
    if not 0.1 <= width_ratio <= 1.0:
        raise ValueError(f"width_ratio 应在 0.1~1.0 之间，当前值: {width_ratio}")
    if "{num}" not in number_format:
        raise ValueError("number_format 必须包含 {num} 占位符，如 \"图{num}\"")
    if label_position not in ("above", "below"):
        raise ValueError('label_position 必须为 "above" 或 "below"')

    if output_path is None:
        base, ext = os.path.splitext(docx_path)
        output_path = f"{base}_images_formatted{ext}"

    # ── 打开文档 ──
    doc = Document(docx_path)

    # ── 计算目标图片宽度 (EMU) ──
    base_target_width_emu = _calc_target_width(doc, width_ratio)
    image_ratios = image_ratios or {}

    # ── 扫描所有图片段落 ──
    image_entries = _scan_image_paragraphs(doc)
    if not image_entries:
        doc.save(output_path)
        return output_path, 0

    # ── 逐张处理 ──
    fig_number = 1

    for idx, entry in enumerate(image_entries):
        try:
            # 计算该图片的独立比例
            img_ratio = image_ratios.get(idx, image_ratios.get(str(idx)))
            if img_ratio is not None:
                target_width_emu = int(base_target_width_emu * img_ratio / width_ratio) if width_ratio > 0 else base_target_width_emu
            else:
                target_width_emu = base_target_width_emu

            _process_single_image(
                entry=entry,
                fig_number=fig_number,
                number_format=number_format,
                target_width_emu=target_width_emu,
                doc=doc,
                label_position=label_position,
                alignment=alignment,
            )
            fig_number += 1
        except Exception as e:
            print(f"Warning: failed to process image #{fig_number}: {e}")
            continue

    # ── 保存 ──
    doc.save(output_path)
    return output_path, fig_number - 1


# ── 内部函数 ──────────────────────────────────────────

def _calc_target_width(doc: Document, ratio: float) -> int:
    """根据第一节页边距和页面宽度，计算目标图片宽度（EMU）。"""
    section = doc.sections[0]
    page_w = section.page_width      # 页面宽 (EMU 背后是 Length)
    left_m = section.left_margin
    right_m = section.right_margin
    usable = page_w - left_m - right_m
    return int(usable * ratio)


def _scan_image_paragraphs(doc: Document) -> List[Dict]:
    """扫描文档，找出所有含图片的段落及其上下文。

    返回列表，每项包含:
      - para_idx:   图片段落在 doc.paragraphs 中的索引
      - paragraph:  图片所在 Paragraph 对象
      - shape:      对应的 InlineShape（取第一个）
      - label_para: 标签段落（已有"图X"样式的相邻段落），可为 None
      - caption_para: 图注段落（图片下方短文本段落），可为 None
    """
    paragraphs = list(doc.paragraphs)
    entries: List[Dict] = []
    seen_indices: set = set()

    # 方法 1: 通过 InlineShape 反查所属段落
    for shape in doc.inline_shapes:
        try:
            para = _get_shape_parent_paragraph(shape, paragraphs)
            if para is None:
                continue
            idx = paragraphs.index(para)
        except (ValueError, AttributeError):
            continue

        if idx in seen_indices:
            continue
        seen_indices.add(idx)

        entry = {
            "para_idx": idx,
            "paragraph": para,
            "shape": shape,
            "label_para": None,
            "caption_para": None,
        }

        # 检查前后段落
        _attach_context_paragraphs(entry, paragraphs, idx)

        entries.append(entry)

    # 方法 2: 兜底 — 遍历所有段落查找 w:drawing（有些图片可能不在 inline_shapes 中）
    for i, para in enumerate(paragraphs):
        if i in seen_indices:
            continue
        drawings = para._element.findall(qn("w:drawing"))
        if drawings:
            entry = {
                "para_idx": i,
                "paragraph": para,
                "shape": None,  # 没有 InlineShape 对象也能处理
                "label_para": None,
                "caption_para": None,
            }
            _attach_context_paragraphs(entry, paragraphs, i)
            entries.append(entry)

    # 按段落顺序排序
    entries.sort(key=lambda e: e["para_idx"])
    return entries


def _get_shape_parent_paragraph(shape, paragraphs: list):
    """从 InlineShape 的 XML 节点向上找到 <w:p> 父节点，返回对应 Paragraph。"""
    node = shape._inline
    while node is not None:
        if node.tag == qn("w:p"):
            for p in paragraphs:
                if p._element is node:
                    return p
            return None
        node = node.getparent()
    return None


def _attach_context_paragraphs(entry: Dict, paragraphs: list, idx: int):
    """为图片条目关联前后的标签和图注段落。"""
    prev = paragraphs[idx - 1] if idx > 0 else None
    nxt = paragraphs[idx + 1] if idx + 1 < len(paragraphs) else None

    # 前一段：如果看起来像图片标签，关联它
    if prev and prev.text.strip():
        if _looks_like_figure_label(prev.text):
            entry["label_para"] = prev

    # 后一段：短文本 → 可能是图注
    if nxt and nxt.text.strip():
        txt = nxt.text.strip()
        # 如果后一段看起来不像标签且长度 < 200，视为图注
        if not _looks_like_figure_label(txt) and len(txt) < 200:
            entry["caption_para"] = nxt
        elif _looks_like_figure_label(txt) and entry["label_para"] is None:
            entry["label_para"] = nxt


def _looks_like_figure_label(text: str) -> bool:
    """判断文本是否为图片标签（"图X" 或 "Figure X" 模式）。"""
    return bool(re.match(
        r"^\s*(图|Figure|Fig\.?)\s*\d+",
        text.strip(),
        re.IGNORECASE,
    ))


def _strip_existing_label(text: str) -> str:
    """去掉现有的图片标签前缀，返回纯描述文本。"""
    return re.sub(
        r"^\s*(图|Figure|Fig\.?)\s*\d+\s*[：:.\-\s]*",
        "",
        text.strip(),
        flags=re.IGNORECASE,
    )


def _process_single_image(
    entry: Dict,
    fig_number: int,
    number_format: str,
    target_width_emu: int,
    doc: Document,
    label_position: str = "above",
    alignment: Optional[str] = None,
):
    """处理单张图片：缩放、编号、图注格式、间距。"""
    para = entry["paragraph"]
    shape = entry.get("shape")
    label_para = entry.get("label_para")
    caption_para = entry.get("caption_para")

    fig_label = number_format.format(num=fig_number)

    # ── 解析对齐 ──
    _align = WD_ALIGN_PARAGRAPH.CENTER  # 默认居中
    if alignment and alignment.upper() in ("LEFT", "CENTER", "RIGHT"):
        _align = getattr(WD_ALIGN_PARAGRAPH, alignment.upper())

    # ── 1. 缩放图片 ──
    if shape is not None:
        ow = shape.width   # EMU
        oh = shape.height
        if ow > 0:
            scale = target_width_emu / ow
            shape.width = target_width_emu
            shape.height = int(oh * scale)

    # ── 2. 图片段落格式 ──
    para.alignment = _align
    # OOXML 层兜底：确保对齐属性正确写入
    pPr = para._element.get_or_add_pPr()
    jc = pPr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        pPr.append(jc)
    _align_str = alignment.upper() if (alignment and alignment.upper() in ("LEFT", "CENTER", "RIGHT")) else "center"
    jc.set(qn("w:val"), _align_str.lower())
    pf = para.paragraph_format
    # 0.5 行间距 ≈ 五号字体高度 (10.5pt) 的一半
    pf.space_before = Pt(5)
    pf.space_after = Pt(5)
    _set_keep_together(para)

    # ── 3. 处理标签和图注 ──
    if label_para is not None:
        # 更新已有标签段落
        existing_desc = _strip_existing_label(label_para.text)
        _clear_and_fill_label(label_para, fig_label, existing_desc)
        label_para.alignment = _align
        _set_keep_together(label_para)

    elif caption_para is not None and label_position == "below":
        # 没有独立标签，图注段落兼作标签（放在图片下方）
        existing_text = caption_para.text.strip()
        existing_text = _strip_existing_label(existing_text)
        _clear_and_fill_label(caption_para, fig_label, existing_text)
        caption_para.alignment = _align
        _set_keep_together(caption_para)
        caption_para = None  # 已处理，避免重复格式化

    else:
        # 没有标签也没有图注 → 在图片上方插入编号段落
        new_label = _insert_paragraph_before(para, doc)
        _clear_and_fill_label(new_label, fig_label, "")
        new_label.alignment = _align
        _set_keep_together(new_label)

    # ── 4. 格式化图注段落 ──
    if caption_para is not None:
        caption_para.alignment = _align
        for run in caption_para.runs:
            _format_caption_run(run)
        _set_keep_together(caption_para)


def _clear_and_fill_label(para, label_text: str, description: str):
    """清空段落并填充：『图X』(加粗) + 描述文字(常规)。"""
    para.text = ""  # 清空所有 runs
    # 编号 run
    label_run = para.add_run(label_text)
    _format_label_run(label_run)
    # 描述 run
    if description:
        spacer = para.add_run(" ")
        spacer.font.size = SIZE_LABEL
        desc_run = para.add_run(description)
        _format_caption_run(desc_run)


def _insert_paragraph_before(target_para, doc: Document):
    """在目标段落前插入一个新段落，返回新 Paragraph 对象。"""
    new_p = OxmlElement("w:p")
    target_para._element.addprevious(new_p)
    # 重新实例化 Paragraph 对象以方便操作
    from docx.text.paragraph import Paragraph
    return Paragraph(new_p, doc)


def _format_label_run(run):
    """格式化编号 run：宋体 / 五号 / 加粗。"""
    run.font.name = FONT_LABEL
    run.font.size = SIZE_LABEL
    run.bold = True
    _set_east_asian(run, FONT_LABEL)


def _format_caption_run(run):
    """格式化图注 run：宋体 / 五号 / 不加粗。"""
    run.font.name = FONT_CAPTION
    run.font.size = SIZE_CAPTION
    run.bold = False
    _set_east_asian(run, FONT_CAPTION)


def _set_east_asian(run, font_name: str):
    """设置 run 的东亚字体 (w:eastAsia)。"""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:eastAsia"), font_name)


def _set_keep_together(para):
    """设置段落 XML 属性，防止跨页断档：keepNext + keepLines。"""
    pPr = para._element.get_or_add_pPr()

    for tag in ("w:keepNext", "w:keepLines"):
        existing = pPr.find(qn(tag))
        if existing is None:
            elem = OxmlElement(tag)
            pPr.append(elem)


# ── 图片提取（供前端预览用）────────────────────────────

def extract_images(docx_path: str) -> tuple[list[dict], int]:
    """从 docx 中提取所有图片为 base64 数据。

    Args:
        docx_path: DOCX 文件路径

    Returns:
        (image_list, page_width_usable_emu)
        image_list 每项: {index, base64, width_emu, height_emu, content_type}
    """
    import base64

    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"文件不存在: {docx_path}")

    doc = Document(docx_path)
    page_width_usable = _calc_target_width(doc, 1.0)

    images = []

    for shape in doc.inline_shapes:
        try:
            # 获取图片尺寸（EMU）
            width_emu = int(shape.width)
            height_emu = int(shape.height)
        except Exception:
            continue  # 非标准形状（画布/图表等），跳过

        # 通过 XML 获取图片引用
        try:
            blip = shape._inline.find(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
            )
            if blip is None:
                continue

            embed = blip.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
            )
            if embed is None or embed not in doc.part.rels:
                continue

            rel = doc.part.rels[embed]
            from docx.opc.constants import RELATIONSHIP_TYPE as RT
            if rel.reltype != RT.IMAGE:
                continue

            image_part = rel.target_part
            image_bytes = image_part.blob
            content_type = image_part.content_type or "image/png"

        except Exception:
            continue

        # Base64 编码
        b64 = base64.b64encode(image_bytes).decode("ascii")
        data_uri = f"data:{content_type};base64,{b64}"

        # 限制单张图片最大 5MB
        if len(data_uri) > 6_000_000:
            continue

        images.append({
            "index": len(images),
            "base64": data_uri,
            "width_emu": width_emu,
            "height_emu": height_emu,
            "content_type": content_type,
        })

    return images, page_width_usable


# ── 自检入口 ──────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python engine.py <docx文件路径> [宽度比例] [编号格式]")
        print("示例: python engine.py paper.docx 0.7 \"图{num}\"")
        sys.exit(1)

    path_arg = sys.argv[1]
    ratio_arg = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
    fmt_arg = sys.argv[3] if len(sys.argv) > 3 else "图{num}"

    try:
        out, count = auto_format_images(path_arg, width_ratio=ratio_arg, number_format=fmt_arg)
        print(f"✅ 处理完成: {out}")
        print(f"   共处理 {count} 张图片")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        sys.exit(1)
