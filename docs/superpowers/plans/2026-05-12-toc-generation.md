# 目录自动生成与格式设置

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**目标：** 上传论文后检测/生成目录；格式面板新增目录设置区；排版引擎生成带占位页码的目录；预览页显示目录条目。

**架构：** 扩展 FormatSettings/FormatSettingsEnabled 新增 TOC 字段；docx_processor 新增关键词检测 + 目录生成；前端面板新增"目录设置"Section；预览页 TOC 条目以特殊 level 渲染。

**技术栈：** React + TypeScript + FastAPI + Pydantic + python-docx

**兼容性：** 所有新增字段均为 additive，Pydantic 默认值保证向后兼容。TOC 段落跳过表格/图片保护逻辑。FormatTooltip 无需改动。

---

### 任务 1：后端 Schema 扩展 TOC 字段

**文件：**
- 修改：`backend/app/schemas/job.py`

- [ ] **步骤 1：FormatSettings 新增 6 个 TOC 字段**

在 `footer` 字段之后，`class CustomizeRequest` 之前插入：

```python
    # TOC settings
    toc_enabled: bool = True
    toc_title: FormatSettingItem = FormatSettingItem(font_name="黑体", font_size=16, bold=True, alignment="center", line_spacing=1.5)
    toc_entry: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=12, bold=False, alignment="left", line_spacing=1.5, first_line_indent=0)
    toc_show_page_numbers: bool = True
    toc_page_number_align: str = "right"
    toc_include_h3: bool = False
```

- [ ] **步骤 2：FormatSettingsEnabled 新增 2 个 TOC enabled 字段**

在 `footer` 字段之后插入：

```python
    toc_title: FormatSettingItemEnabled = FormatSettingItemEnabled()
    toc_entry: FormatSettingItemEnabled = FormatSettingItemEnabled()
```

- [ ] **步骤 3：验证 schema 导入**

```bash
cd backend && python -c "from app.schemas.job import FormatSettings, FormatSettingsEnabled; s=FormatSettings(); e=FormatSettingsEnabled(); print('toc_enabled:', s.toc_enabled); print('toc_title.font_name:', s.toc_title.font_name); print('enabled toc_title:', e.toc_title.font_name); print('OK')"
```
预期：`toc_enabled: True`, `toc_title.font_name: 黑体`, `enabled toc_title: True`

---

### 任务 2：docx_processor — TOC 检测和生成

**文件：**
- 修改：`backend/app/services/docx_processor.py`

- [ ] **步骤 1：新增 `_detect_toc(doc)` 函数**

在前 20 个段落中搜索"目录"关键词：

```python
def _detect_toc(doc) -> dict:
    """Detect if the document has a TOC. Returns {has_toc, start_idx, end_idx}."""
    for i, para in enumerate(doc.paragraphs):
        if i > 20:
            break
        text = para.text.strip().replace(" ", "")
        if "目录" in text:
            # Find end of TOC: next Heading paragraph
            end = i + 1
            for j in range(i + 1, min(len(doc.paragraphs), i + 50)):
                if doc.paragraphs[j].style and "Heading" in (doc.paragraphs[j].style.name or ""):
                    end = j
                    break
            return {"has_toc": True, "start_idx": i, "end_idx": end}
    return {"has_toc": False, "start_idx": -1, "end_idx": -1}
```

- [ ] **步骤 2：新增 `_generate_toc(doc, structure, toc_settings, insert_idx)` 函数**

在指定位置插入目录标题和条目。toc_settings 来自 FormatSettings 的 TOC 字段：

```python
def _generate_toc(doc, structure, toc_settings, insert_idx: int):
    """Generate TOC at insert_idx position. toc_settings is a dict with toc_* fields."""
    if not toc_settings.get("toc_enabled", True):
        return

    sections = structure.get("sections", [])
    include_h3 = toc_settings.get("toc_include_h3", False)
    show_pn = toc_settings.get("toc_show_page_numbers", True)
    pn_align = toc_settings.get("toc_page_number_align", "right")

    # Insert TOC title paragraph at insert_idx
    title_para = doc.paragraphs[insert_idx]._element
    new_para = OxmlElement('w:p')
    title_para.addprevious(new_para)
    # ... insert title text with toc_title format
```

由于 python-docx 操作较复杂，采用简化方案：使用 `doc.add_paragraph()` 的 `before` 参数或直接用 lxml 操作 XML。实际实现：

```python
def _generate_toc(doc, structure, custom_settings, enabled_settings):
    """Generate TOC at the beginning of the document."""
    title_cfg = custom_settings.toc_title
    entry_cfg = custom_settings.toc_entry

    # Find insertion point: before first heading-style paragraph
    insert_before = None
    for para in doc.paragraphs:
        if para.style and "Heading" in (para.style.name or ""):
            insert_before = para
            break

    # Build TOC entries
    entries = []
    for s in structure.get("sections", []):
        level = s.get("level", 1)
        if level > 2 and not custom_settings.toc_include_h3:
            continue
        entries.append((level, s.get("title", "")))

    if not entries:
        return

    # Insert TOC title
    if insert_before:
        toc_title_para = insert_before.insert_paragraph_before("")
    else:
        toc_title_para = doc.add_paragraph("")
    run = toc_title_para.add_run("目  录")
    _apply_toc_format(run, toc_title_para, title_cfg, enabled_settings.toc_title if enabled_settings else None)

    # Insert TOC entries
    for level, title in entries:
        indent = "    " * (level - 1)
        line = f"{indent}{title}"
        if custom_settings.toc_show_page_numbers:
            line += "  [页码]"
        if insert_before:
            p = insert_before.insert_paragraph_before("")
        else:
            p = doc.add_paragraph("")
        run = p.add_run(line)
        _apply_toc_format(run, p, entry_cfg, enabled_settings.toc_entry if enabled_settings else None)

    # Add a blank line after TOC
    if insert_before:
        p = insert_before.insert_paragraph_before("")
    else:
        p = doc.add_paragraph("")
```

- [ ] **步骤 3：新增 `_apply_toc_format(run, para, cfg, enabled)` 辅助函数**

```python
def _apply_toc_format(run, para, cfg, enabled):
    """Apply TOC-specific formatting."""
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
```

- [ ] **步骤 4：apply_formatting 中集成 TOC 逻辑**

在页面设置之后、段落循环之前：

```python
    # TOC handling
    toc_info = _detect_toc(doc)
    structure["has_toc"] = toc_info["has_toc"]

    if custom_settings and custom_settings.toc_enabled:
        # Remove existing TOC paragraphs if present and replacing
        if toc_info["has_toc"]:
            # Skip TOC paragraphs during formatting (they'll be regenerated)
            pass
        # Generate new TOC
        _generate_toc(doc, structure, custom_settings, enabled_settings)
```

- [ ] **步骤 5：段落循环中跳过 TOC 段落**

```python
    toc_skip_range = range(toc_info["start_idx"], toc_info["end_idx"] + 1) if toc_info["has_toc"] else range(0)
    for i, para in enumerate(doc.paragraphs):
        if i in toc_skip_range:
            continue
        # ... existing logic
```

- [ ] **步骤 6：验证后端导入**

```bash
cd backend && python -c "from app.main import app; print('OK')"
```

---

### 任务 3：extract_formatted_content 标记目录

**文件：**
- 修改：`backend/app/services/docx_processor.py`

- [ ] **步骤 1：检测并标记 TOC 条目到预览数据**

在 `extract_formatted_content` 中，将 TOC 相关段落以特殊 level（`-1` 表示目录标题，`-2` 表示目录条目）加入返回结果：

```python
    # Before the section loop, check for TOC
    toc_info = _detect_toc(doc)
    if toc_info["has_toc"]:
        toc_section = {
            "level": -1,
            "title": "目录",
            "content": "",
            "markers": [],
        }
        toc_body = []
        for i in range(toc_info["start_idx"], toc_info["end_idx"]):
            if i < len(doc.paragraphs):
                t = doc.paragraphs[i].text.strip()
                if t and t != "目录" and "目  录" not in t.replace(" ", ""):
                    toc_body.append(t)
        toc_section["content"] = "\n".join(toc_body)
        result_sections.insert(0, toc_section)  # prepend
```

- [ ] **步骤 2：验证导入**

（同上）

---

### 任务 4：前端类型扩展

**文件：**
- 修改：`frontend/src/types/index.ts`

- [ ] **步骤 1：FormatSettings 接口新增 TOC 字段**

```typescript
export interface FormatSettings {
  // ... existing fields ...
  toc_enabled: boolean
  toc_title: FormatSettingItem
  toc_entry: FormatSettingItem
  toc_show_page_numbers: boolean
  toc_page_number_align: string
  toc_include_h3: boolean
}
```

- [ ] **步骤 2：FormatSettingsEnabled 接口新增**

```typescript
export interface FormatSettingsEnabled {
  // ... existing fields ...
  toc_title: FormatSettingItemEnabled
  toc_entry: FormatSettingItemEnabled
}
```

- [ ] **步骤 3：DEFAULT_FORMAT_SETTINGS 新增 TOC 默认值**

```typescript
  // (at the end of DEFAULT_FORMAT_SETTINGS, before closing })
  toc_enabled: true,
  toc_title: { font_name: "黑体", font_size: 16, bold: true, alignment: "center", line_spacing: 1.5, first_line_indent: 0, space_before: 0, space_after: 0 },
  toc_entry: { font_name: "宋体", font_size: 12, bold: false, alignment: "left", line_spacing: 1.5, first_line_indent: 0, space_before: 0, space_after: 0 },
  toc_show_page_numbers: true,
  toc_page_number_align: "right",
  toc_include_h3: false,
```

- [ ] **步骤 4：DEFAULT_ENABLED_SETTINGS 新增**

```typescript
  toc_title: { ...DEFAULT_ITEM_ENABLED },
  toc_entry: { ...DEFAULT_ITEM_ENABLED },
```

- [ ] **步骤 5：TypeScript 编译检查**

```bash
npx tsc --noEmit --pretty
```

---

### 任务 5：FormatSettingsPanel 新增"目录设置"区域

**文件：**
- 修改：`frontend/src/components/format/FormatSettingsPanel.tsx`

- [ ] **步骤 1：在"参考文献" Section 之后插入"目录设置" Section**

```tsx
      {/* TOC Settings */}
      <Section title="目录设置" expanded={expanded.toc} onToggle={() => toggle("toc")}>
        <div className="space-y-2">
          {/* Master toggle */}
          <div className="flex items-center gap-2">
            <Checkbox
              checked={settings.toc_enabled}
              onCheckedChange={(v) => onChange({ ...settings, toc_enabled: !!v })}
              className="h-3.5 w-3.5"
            />
            <Label className="text-xs font-medium">生成目录</Label>
          </div>

          {settings.toc_enabled && (
            <>
              <div className="border-t pt-2">
                <p className="text-[10px] text-muted-foreground mb-1">目录标题格式</p>
                <ItemEditor
                  item={settings.toc_title}
                  enabled={enabled.toc_title}
                  onChange={(v) => update("toc_title", v.field, v.value)}
                  onEnabledChange={(v) => updateEnabled("toc_title", v.field, v.value)}
                />
              </div>
              <div className="border-t pt-2">
                <p className="text-[10px] text-muted-foreground mb-1">目录条目格式</p>
                <ItemEditor
                  item={settings.toc_entry}
                  enabled={enabled.toc_entry}
                  onChange={(v) => update("toc_entry", v.field, v.value)}
                  onEnabledChange={(v) => updateEnabled("toc_entry", v.field, v.value)}
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={settings.toc_show_page_numbers}
                  onCheckedChange={(v) => onChange({ ...settings, toc_show_page_numbers: !!v })}
                  className="h-3.5 w-3.5"
                />
                <Label className="text-xs">显示页码</Label>
              </div>
              {settings.toc_show_page_numbers && (
                <div>
                  <Label className="text-[10px] text-muted-foreground">页码对齐</Label>
                  <Select value={settings.toc_page_number_align} onValueChange={(v) => onChange({ ...settings, toc_page_number_align: v })}>
                    <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="left">左对齐</SelectItem>
                      <SelectItem value="right">右对齐</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={settings.toc_include_h3}
                  onCheckedChange={(v) => onChange({ ...settings, toc_include_h3: !!v })}
                  className="h-3.5 w-3.5"
                />
                <Label className="text-xs">包含三级标题</Label>
              </div>
            </>
          )}
        </div>
      </Section>
```

- [ ] **步骤 2：TypeScript 编译 + Vite 构建**

```bash
npx tsc --noEmit --pretty && npx vite build --logLevel warn
```

---

### 任务 6：ResultPreview 渲染 TOC 条目

**文件：**
- 修改：`frontend/src/components/result/ResultPreview.tsx`

- [ ] **步骤 1：TOC 条目特殊渲染**

当 section 的 `level === -1` 时显示为目录标题：
```tsx
{section.level === -1 ? (
  <div className="text-center py-2">
    <h3 className="text-lg font-bold">{section.title}</h3>
  </div>
) : (
  // existing section rendering
)}
```

TOC 条目（level === -1 时的 content 行）悬停时显示 TOC 条目格式。

- [ ] **步骤 2：编译验证**

---

### 任务 7：端到端验证

- [ ] **步骤 1：后端 + 前端构建**

```bash
cd backend && python -c "from app.main import app; print('Backend OK')"
cd frontend && npx tsc --noEmit --pretty && npx vite build --logLevel warn
```

- [ ] **步骤 2：全功能验证清单**

1. 默认模板加载 — 目录设置区显示默认值 ✓
2. 字体字号下拉 — 目录标题/条目使用相同下拉组件 ✓
3. 勾选框 — 目录标题/条目各字段可独立勾选/取消 ✓
4. 悬停格式 — 预览页目录条目悬停显示 TOC 格式 ✓
5. 表格/图片保护 — TOC 生成不干扰表格图片 ✓
6. 上传含目录论文 — 检测到已有目录 ✓
7. 上传无目录论文 — 自动生成目录（标题+条目+[页码]） ✓
8. 取消"生成目录" — 排版跳过目录 ✓
9. 取消"显示页码" — 条目无 [页码] 标记 ✓
10. 勾选"包含三级标题" — H3 也出现在目录中 ✓
