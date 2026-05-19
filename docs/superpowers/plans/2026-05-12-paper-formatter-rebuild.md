# 论文排版网站 修复与重构计划

> **目标：** 注入统一论文格式规范到排版引擎，重构预览界面为仅显示排版后内容+前进/后退导航

**技术栈：** React 18 + TypeScript + Vite + shadcn/ui + Tailwind CSS / Python FastAPI + SQLite / python-docx / DeepSeek-V4

---

## 格式规范（必须严格遵循）

| 元素 | 字体 | 字号 | 加粗 | 对齐 | 行距 | 其他 |
|------|------|------|------|------|------|------|
| 一级标题 | 黑体 | 16pt | 是 | 居中 | - | - |
| 二级标题 | 黑体 | 14pt | 是 | 左对齐 | - | - |
| 三级标题 | 黑体 | 12pt | 是 | 左对齐 | - | - |
| 正文 | 宋体 | 12pt | 否 | 两端对齐 | 1.5倍 | 首行缩进2字符 |
| 图注/表注 | 宋体 | 10.5pt | 否 | 居中 | - | - |
| 页眉/页脚 | 宋体 | 9pt | 否 | 居中 | - | - |
| 参考文献条目 | 宋体 | 10.5pt | 否 | - | 单倍 | "参考文献"标题为一级标题格式 |

页边距：上2.54cm 下2.54cm 左3.17cm 右3.17cm，页眉1.5cm 页脚1.75cm

---

## Phase 1: Backend 格式标准引擎

**文件：**
- 新建：`backend/app/services/format_standards.py`
- 修改：`backend/app/services/docx_processor.py`
- 修改：`backend/app/services/pdf_processor.py`
- 修改：`backend/app/services/ai_analyzer.py`
- 修改：`backend/app/schemas/job.py`

### Task 1.1: 创建格式标准模块

```python
# backend/app/services/format_standards.py

from dataclasses import dataclass
from docx.shared import Pt, Cm, Inches, Emu
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH

@dataclass
class PageSettings:
    margin_top: float = 2.54       # cm
    margin_bottom: float = 2.54    # cm
    margin_left: float = 3.17      # cm
    margin_right: float = 3.17     # cm
    header_distance: float = 1.5   # cm
    footer_distance: float = 1.75  # cm

@dataclass
class FontSpec:
    name: str
    name_ascii: str  # fallback for Latin chars
    size: Pt
    bold: bool

@dataclass
class ParaSpec:
    font: FontSpec
    alignment: int  # WD_ALIGN_PARAGRAPH
    line_spacing: float  # multiplier
    first_line_indent: Pt | None  # None = no indent
    space_before: Pt
    space_after: Pt

# 字体定义
FONT_HEITI = "黑体"
FONT_SONGTI = "宋体"

# 一级标题：黑体 16pt 加粗 居中
H1_SPEC = ParaSpec(
    font=FontSpec(FONT_HEITI, "Arial", Pt(16), True),
    alignment=WD_ALIGN_PARAGRAPH.CENTER,
    line_spacing=1.5,
    first_line_indent=None,
    space_before=Pt(12),
    space_after=Pt(6),
)

# 二级标题：黑体 14pt 加粗 左对齐
H2_SPEC = ParaSpec(
    font=FontSpec(FONT_HEITI, "Arial", Pt(14), True),
    alignment=WD_ALIGN_PARAGRAPH.LEFT,
    line_spacing=1.5,
    first_line_indent=None,
    space_before=Pt(10),
    space_after=Pt(4),
)

# 三级标题：黑体 12pt 加粗 左对齐
H3_SPEC = ParaSpec(
    font=FontSpec(FONT_HEITI, "Arial", Pt(12), True),
    alignment=WD_ALIGN_PARAGRAPH.LEFT,
    line_spacing=1.5,
    first_line_indent=None,
    space_before=Pt(8),
    space_after=Pt(4),
)

# 正文：宋体 12pt 两端对齐 1.5倍行距 首行缩进2字符
BODY_SPEC = ParaSpec(
    font=FontSpec(FONT_SONGTI, "Times New Roman", Pt(12), False),
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
    line_spacing=1.5,
    first_line_indent=Pt(24),  # 2 chars at 12pt
    space_before=Pt(0),
    space_after=Pt(0),
)

# 图注/表注：宋体 10.5pt 居中
CAPTION_SPEC = ParaSpec(
    font=FontSpec(FONT_SONGTI, "Times New Roman", Pt(10.5), False),
    alignment=WD_ALIGN_PARAGRAPH.CENTER,
    line_spacing=1.5,
    first_line_indent=None,
    space_before=Pt(2),
    space_after=Pt(2),
)


def apply_page_settings(doc):
    """Apply page margins and header/footer distance to document."""
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)
        section.header_distance = Cm(1.5)
        section.footer_distance = Cm(1.75)


def apply_paragraph_format(para, spec: ParaSpec):
    """Apply font, alignment, spacing, and indent to a paragraph."""
    pf = para.paragraph_format
    pf.alignment = spec.alignment
    pf.line_spacing = spec.line_spacing
    pf.space_before = spec.space_before
    pf.space_after = spec.space_after
    if spec.first_line_indent is not None:
        pf.first_line_indent = spec.first_line_indent
    for run in para.runs:
        run.font.name = spec.font.name
        run.font.size = spec.font.size
        run.font.bold = spec.font.bold
        # Set East-Asian font
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
        if rFonts is None:
            from lxml import etree
            rFonts = etree.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
        rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia', spec.font.name)
```

### Task 1.2: 重写 docx_processor.py

Rewrite `apply_formatting()` to:
1. Apply page settings (margins)
2. For each paragraph, match against AI-detected sections
3. Apply heading spec to matched headings
4. Apply body spec to all non-heading paragraphs
5. Detect figure/table captions and apply caption spec

### Task 1.3: 更新 ai_analyzer.py system prompt

Add formatting standard requirements to the system prompt so AI knows what constitutes a section.

---

## Phase 2: Backend 预览 API

**文件：**
- 新建：`backend/app/routers/preview.py`
- 修改：`backend/app/main.py`
- 修改：`backend/app/services/docx_processor.py` (add extract_formatted_content)

### Task 2.1: 创建 preview 路由

New endpoint: `GET /api/preview/{job_id}` → returns structured formatted content:
```json
{
  "title": "论文标题",
  "sections": [
    {"level": 1, "title": "第一章", "paragraphs": ["段落1", "段落2"]},
    ...
  ]
}
```

### Task 2.2: 注册路由

Add preview router to main.py.

---

## Phase 3: Frontend 预览重构

**文件：**
- 修改：`frontend/src/pages/ProcessPage.tsx`
- 重写：`frontend/src/components/result/ResultPreview.tsx`
- 修改：`frontend/src/types/index.ts`
- 修改：`frontend/src/services/api.ts`
- 修改：`frontend/src/hooks/useFormatting.ts`

### Task 3.1: 更新类型定义

Add `PreviewData` type with sections and navigation info.

### Task 3.2: 更新 API service

Add `getPreview(jobId)` method.

### Task 3.3: 重写 ResultPreview

New design:
- Top bar: "排版结果" title + download button
- Main area: rendered formatted content, section by section
- Bottom bar: "上一节" / "下一节" navigation buttons
- Current section indicator ("第 3/12 节")

### Task 3.4: 更新 useFormatting hook

Fetch preview data when state becomes "done".

---

## Phase 4: 构建与验证

1. Backend restart + route verification
2. Frontend build
3. E2E test: upload → analyze → format → preview → download
