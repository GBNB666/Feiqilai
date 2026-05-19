# 排版时保护表格和图片，预览页可视化标记

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**目标：** 排版引擎跳过表格和图片不做修改；预览页在段落流中插入占位框标记位置。

**架构：** 扩展 `PreviewSection` schema 新增 `markers` 数组；`docx_processor.apply_formatting` 跳过表格/图片段落；`extract_formatted_content` 检测表格/图片并返回 markers；前端 `ResultPreview` 在段落间渲染占位框。

**技术栈：** React + TypeScript + FastAPI + Pydantic + python-docx

---

### 任务 1：后端 Schema 扩展 PreviewSection

**文件：**
- 修改：`backend/app/schemas/job.py`

- [ ] **步骤 1：新增 ContentMarker 类型，扩展 PreviewSection**

```python
class ContentMarker(BaseModel):
    type: str  # "table" | "image"
    index: int  # 该section内的序号
    description: str  # "3行×4列" | "480×320px"
    rows: int | None = None
    cols: int | None = None
    width_px: int | None = None
    height_px: int | None = None


class PreviewSection(BaseModel):
    level: int
    title: str
    content: str
    markers: list[ContentMarker] = []
```

`PreviewResponse` 中的 sections 类型会自动跟随。

- [ ] **步骤 2：验证导入**

```bash
cd backend && python -c "from app.schemas.job import ContentMarker, PreviewSection; s = PreviewSection(level=1, title='test', content='', markers=[ContentMarker(type='table', index=0, description='3行×4列', rows=3, cols=4)]); print(s.model_dump())"
```
预期：正确序列化

---

### 任务 2：排版引擎跳过表格和图片

**文件：**
- 修改：`backend/app/services/docx_processor.py`

- [ ] **步骤 1：apply_formatting 中跳过表格**

在段落循环中，检查段落是否属于表格（通过 `para._element` 的父元素判断），跳过表格内段落：

```python
for para in doc.paragraphs:
    # Skip paragraphs inside tables — tables are preserved as-is
    parent_tag = para._element.getparent().tag.split('}')[-1] if para._element.getparent() is not None else ''
    if parent_tag == 'tc':
        continue
    text = para.text.strip()
    ...
```

- [ ] **步骤 2：跳过包含图片的段落**

检查段落中是否包含 drawing/pict 元素（图片），跳过：

```python
    # Skip paragraphs that contain images
    nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
             'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
             'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    has_image = len(para._element.findall('.//wp:inline', nsmap)) > 0 or \
                len(para._element.findall('.//wp:anchor', nsmap)) > 0 or \
                len(para._element.findall('.//w:drawing', nsmap)) > 0
    if has_image:
        continue
```

- [ ] **步骤 3：不修改 doc.tables 的任何属性**

在 apply_formatting 末尾确认不调用任何修改 tables 的代码（当前代码已不操作 tables，此步骤为验证）。

- [ ] **步骤 4：验证后端导入**

```bash
cd backend && python -c "from app.main import app; print('OK')"
```

---

### 任务 3：extract_formatted_content 检测表格/图片

**文件：**
- 修改：`backend/app/services/docx_processor.py`

- [ ] **步骤 1：重写 extract_formatted_content 增加表格/图片检测**

```python
def extract_formatted_content(file_path: str, structure: dict) -> list[dict]:
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

    # Build para → section map from start_markers
    para_section_map = {}
    for s in sections:
        marker = s.get("start_marker", "")
        for i, para in enumerate(doc.paragraphs):
            if marker and marker in para.text:
                para_section_map[i] = s

    # Also map tables to the nearest preceding section paragraph
    table_section_map = {}
    for ti, table in enumerate(doc.tables):
        # Find the nearest paragraph before this table
        # Simple heuristic: assign to the most recent section
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                for para in cell.paragraphs:
                    # Find which section this paragraph belongs to (if any)
                    pass
        # Use a simpler approach: last opened section
        table_section_map[ti] = len(result_sections) - 1 if result_sections else 0

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            # Check if this empty paragraph contains an image
            has_image = len(para._element.findall('.//wp:inline', nsmap)) > 0 or \
                        len(para._element.findall('.//wp:anchor', nsmap)) > 0
            if has_image and current_section is not None:
                idx = marker_idx["image"]
                marker_idx["image"] += 1
                # Get image dimensions from drawing element
                w, h = _get_image_dims(para._element, nsmap)
                current_markers.append({
                    "type": "image", "index": idx,
                    "description": f"图片：宽{w}px×高{h}px" if w else "图片（嵌入）",
                    "rows": None, "cols": None,
                    "width_px": w, "height_px": h,
                })
            continue

        if i in para_section_map:
            # Save previous section
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

    # Check for tables after the last paragraph
    if doc.tables and current_section is not None:
        for table in doc.tables:
            rows = len(table.rows)
            cols = max(len(row.cells) for row in table.rows)
            idx = marker_idx["table"]
            marker_idx["table"] += 1
            current_markers.append({
                "type": "table", "index": idx,
                "description": f"表格：{rows}行×{cols}列",
                "rows": rows, "cols": cols,
                "width_px": None, "height_px": None,
            })

    # Save last section
    if current_section is not None:
        current_section["content"] = "\n".join(current_body)
        current_section["markers"] = current_markers
        result_sections.append(current_section)

    if not result_sections:
        all_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        result_sections = [{"level": 0, "title": structure.get("title", "正文"), "content": all_text, "markers": []}]

    return result_sections


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
```

有关表格位置的更准确检测：由于 python-docx 的表格与段落是分离的（`doc.tables` 独立于 `doc.paragraphs`），表格在文本流中的位置需要额外判断。采用简单策略：将表格标记附加到当前 section 的 markers 末尾。

- [ ] **步骤 2：验证后端导入**

```bash
cd backend && python -c "from app.main import app; print('OK')"
```

---

### 任务 4：预览 API 返回 markers

**文件：**
- 修改：`backend/app/routers/preview.py`

- [ ] **步骤 1：PreviewResponse 构建时传入 markers**

```python
sections = extract_formatted_content(job.output_path, structure)

return PreviewResponse(
    title=structure.get("title", job.original_filename),
    section_count=len(sections),
    sections=[PreviewSection(**s) for s in sections],
)
```

Schema 已定义 `markers: list[ContentMarker] = []`，`extract_formatted_content` 已返回 markers，此处无需额外修改。

---

### 任务 5：前端类型扩展

**文件：**
- 修改：`frontend/src/types/index.ts`

- [ ] **步骤 1：新增 ContentMarker 接口，扩展 PreviewSection**

```typescript
export interface ContentMarker {
  type: "table" | "image"
  index: number
  description: string
  rows: number | null
  cols: number | null
  width_px: number | null
  height_px: number | null
}

// PreviewSection 扩展 markers 字段
export interface PreviewSection {
  level: number
  title: string
  content: string
  markers: ContentMarker[]
}
```

---

### 任务 6：ResultPreview 渲染占位框

**文件：**
- 修改：`frontend/src/components/result/ResultPreview.tsx`

- [ ] **步骤 1：导入新类型和图标**

```typescript
import { Table, Image } from "lucide-react"
import type { ContentMarker } from "@/types"
```

- [ ] **步骤 2：编写 PlaceholderBlock 组件**

在段落流中的适当位置渲染占位框。将每个 section 的 markers 插入到 content 文本流末尾：

```tsx
function PlaceholderBlock({ marker }: { marker: ContentMarker }) {
  const Icon = marker.type === "table" ? Table : Image
  return (
    <div
      className="border-2 border-dashed border-muted-foreground/30 rounded-lg p-4 my-3 flex items-center gap-3 bg-muted/10"
      onMouseEnter={(e) => {
        // trigger tooltip
      }}
    >
      <Icon className="w-8 h-8 text-muted-foreground/50 shrink-0" />
      <div>
        <p className="text-sm font-medium text-muted-foreground">
          {marker.type === "table" ? "表格" : "图片"}
        </p>
        <p className="text-xs text-muted-foreground/60">{marker.description}</p>
        <p className="text-[10px] text-muted-foreground/40 mt-0.5">
          此元素受保护，排版时原样保留
        </p>
      </div>
    </div>
  )
}
```

- [ ] **步骤 3：在段落流中插入占位框**

在每个 section 的 content 区域渲染时，在正文文本之后、下一个 section 之前插入 markers：

```tsx
{s.content.split("\n").map((line, pi) => (
  <p key={`p-${pi}`} className="mb-1" ...>{line || " "}</p>
))}
{s.markers && s.markers.map((m) => (
  <PlaceholderBlock key={`m-${m.type}-${m.index}`} marker={m} />
))}
```

- [ ] **步骤 4：占位框悬停时显示保护提示**

利用已有的 FormatTooltip 或直接在占位框上显示 tooltip。简单方案：在 PlaceholderBlock 的 onMouseEnter/onMouseLeave 中设置特殊的 tooltipInfo：

```typescript
onMouseEnter={() => {
  setTooltipInfo({ label: "受保护元素", settings: ..., enabled: ..., protected: true })
}}
```

---

### 任务 7：端到端验证

- [ ] **步骤 1：后端导入检查**

```bash
cd backend && python -c "from app.main import app; from app.schemas.job import ContentMarker; print('OK')"
```

- [ ] **步骤 2：前端构建**

```bash
npx tsc --noEmit --pretty && npx vite build --logLevel warn
```

- [ ] **步骤 3：准备测试文档并跑完整流程**

找一个包含表格和图片的 DOCX 文件，上传→分析→排版→预览：
1. 确认输出 DOCX 中表格/图片原样保留
2. 预览页显示表格/图片占位框（虚线边框+图标+说明文字）
3. 悬停占位框显示"此元素受保护"
4. 已有功能（格式设置、勾选框、悬停格式浮窗）正常
