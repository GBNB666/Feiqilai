# 格式编辑面板「是否更改」勾选框

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**目标：** 为格式编辑面板每个子项添加独立的启用/禁用勾选框，排版引擎根据勾选状态决定是否覆盖原文格式。

**架构：** 新增 `FormatSettingsEnabled` 类型（独立于 `FormatSettings` 的布尔镜像结构），前端每个字段旁加 checkbox，后端 customize 接口同时接收 settings 和 enabled，docx_processor 在应用格式前检查 enabled 标志。

**技术栈：** React + TypeScript + shadcn/ui Checkbox + FastAPI + Pydantic v2

---

### 任务 1：后端 Schema 扩展

**文件：**
- 修改：`backend/app/schemas/job.py`

- [ ] **步骤 1：新增 FormatSettingItemEnabled 和 FormatSettingsEnabled**

在 `FormatSettings` 类之后插入：

```python
class FormatSettingItemEnabled(BaseModel):
    font_name: bool = True
    font_size: bool = True
    bold: bool = True
    alignment: bool = True
    line_spacing: bool = True
    first_line_indent: bool = True
    space_before: bool = True
    space_after: bool = True


class FormatSettingsEnabled(BaseModel):
    page_margin_top: bool = True
    page_margin_bottom: bool = True
    page_margin_left: bool = True
    page_margin_right: bool = True
    header_distance: bool = True
    footer_distance: bool = True
    h1: FormatSettingItemEnabled = FormatSettingItemEnabled()
    h2: FormatSettingItemEnabled = FormatSettingItemEnabled()
    h3: FormatSettingItemEnabled = FormatSettingItemEnabled()
    body: FormatSettingItemEnabled = FormatSettingItemEnabled()
    caption: FormatSettingItemEnabled = FormatSettingItemEnabled()
    reference: FormatSettingItemEnabled = FormatSettingItemEnabled()
    header: FormatSettingItemEnabled = FormatSettingItemEnabled()
    footer: FormatSettingItemEnabled = FormatSettingItemEnabled()
```

- [ ] **步骤 2：更新 CustomizeRequest 增加 enabled 字段**

```python
class CustomizeRequest(BaseModel):
    job_id: str
    settings: FormatSettings
    enabled: FormatSettingsEnabled | None = None
```

- [ ] **步骤 3：验证后端 import**

运行：`cd backend && python -c "from app.schemas.job import FormatSettingsEnabled; e = FormatSettingsEnabled(); print(e.model_dump())"`
预期：打印出包含所有字段、全部为 True 的字典

---

### 任务 2：后端排版逻辑适配

**文件：**
- 修改：`backend/app/routers/format.py`
- 修改：`backend/app/services/docx_processor.py`

- [ ] **步骤 1：format.py custom 端点同时存储 settings 和 enabled**

将 customize 端点存储逻辑改为：
```python
import json
payload = {"settings": req.settings.model_dump(), "enabled": req.enabled.model_dump() if req.enabled else {}}
job.user_annotations = json.dumps(payload, ensure_ascii=False)
```

- [ ] **步骤 2：format.py execute 端点读取 enabled 并传入 docx_processor**

```python
ua = json.loads(job.user_annotations or "{}")
custom_settings = FormatSettings(**ua["settings"]) if "settings" in ua else None
custom_enabled = FormatSettingsEnabled(**ua["enabled"]) if "enabled" in ua else None
run_formatting(job, custom_settings, custom_enabled)
```

- [ ] **步骤 3：docx_processor.apply_formatting 接受 enabled 参数**

函数签名增加 `enabled_settings=None`：
```python
def apply_formatting(input_path, output_path, structure, custom_settings=None, enabled_settings=None):
```

- [ ] **步骤 4：逐字段检查 enabled 标志**

在应用页面设置时：
```python
if custom_settings:
    for section in doc.sections:
        if enabled_settings is None or enabled_settings.page_margin_top:
            section.top_margin = Cm(custom_settings.page_margin_top)
        if enabled_settings is None or enabled_settings.page_margin_bottom:
            section.bottom_margin = Cm(custom_settings.page_margin_bottom)
        # ... 同样处理 left, right, header_distance, footer_distance
```

在 `_apply_custom_para` 中增加 `enabled` 参数，逐字段检查：
```python
def _apply_custom_para(para, custom, default_spec, enabled=None):
    pf = para.paragraph_format
    if enabled is None or enabled.alignment:
        pf.alignment = ALIGN_MAP.get(custom.alignment, ...)
    if enabled is None or enabled.line_spacing:
        pf.line_spacing = custom.line_spacing or ...
    # ... 同样处理其他字段
```

在 apply_formatting 中调用时传入对应的 enabled 对象（如 `enabled_settings.h1`、`enabled_settings.body` 等）。

- [ ] **步骤 5：更新 formatter.py**

```python
def run_formatting(job, custom_settings=None, enabled_settings=None):
    # ...
    apply_formatting(job.input_path, job.output_path, structure, custom_settings, enabled_settings)
```

- [ ] **步骤 6：验证后端**

运行：`cd backend && python -c "from app.main import app; print('OK')"`
预期：无 import 错误

---

### 任务 3：前端类型和 API 扩展

**文件：**
- 修改：`frontend/src/types/index.ts`
- 修改：`frontend/src/services/api.ts`

- [ ] **步骤 1：新增前端类型（在 DEFAULT_FORMAT_SETTINGS 之前）**

```typescript
export interface FormatSettingItemEnabled {
  font_name: boolean
  font_size: boolean
  bold: boolean
  alignment: boolean
  line_spacing: boolean
  first_line_indent: boolean
  space_before: boolean
  space_after: boolean
}

export interface FormatSettingsEnabled {
  page_margin_top: boolean
  page_margin_bottom: boolean
  page_margin_left: boolean
  page_margin_right: boolean
  header_distance: boolean
  footer_distance: boolean
  h1: FormatSettingItemEnabled
  h2: FormatSettingItemEnabled
  h3: FormatSettingItemEnabled
  body: FormatSettingItemEnabled
  caption: FormatSettingItemEnabled
  reference: FormatSettingItemEnabled
  header: FormatSettingItemEnabled
  footer: FormatSettingItemEnabled
}

const DEFAULT_ITEM_ENABLED: FormatSettingItemEnabled = {
  font_name: true, font_size: true, bold: true, alignment: true,
  line_spacing: true, first_line_indent: true, space_before: true, space_after: true,
}

export const DEFAULT_ENABLED_SETTINGS: FormatSettingsEnabled = {
  page_margin_top: true, page_margin_bottom: true,
  page_margin_left: true, page_margin_right: true,
  header_distance: true, footer_distance: true,
  h1: { ...DEFAULT_ITEM_ENABLED },
  h2: { ...DEFAULT_ITEM_ENABLED },
  h3: { ...DEFAULT_ITEM_ENABLED },
  body: { ...DEFAULT_ITEM_ENABLED },
  caption: { ...DEFAULT_ITEM_ENABLED },
  reference: { ...DEFAULT_ITEM_ENABLED },
  header: { ...DEFAULT_ITEM_ENABLED },
  footer: { ...DEFAULT_ITEM_ENABLED },
}
```

- [ ] **步骤 2：更新 api.ts 的 customizeSettings**

```typescript
export async function customizeSettings(jobId: string, settings: FormatSettings, enabled?: FormatSettingsEnabled) {
  return http.post("/format/customize", { job_id: jobId, settings, enabled })
}
```

- [ ] **步骤 3：TypeScript 编译检查**

运行：`npx tsc --noEmit --pretty`
预期：零错误

---

### 任务 4：前端 Hook 增加 enabled 状态

**文件：**
- 修改：`frontend/src/hooks/useFormatting.ts`

- [ ] **步骤 1：添加 enabledSettings 状态和更新方法**

```typescript
const [enabledSettings, setEnabledSettings] = useState<FormatSettingsEnabled>(() => {
  const e = { ...DEFAULT_ENABLED_SETTINGS }
  e.h1 = { ...DEFAULT_ITEM_ENABLED }
  e.h2 = { ...DEFAULT_ITEM_ENABLED }
  e.h3 = { ...DEFAULT_ITEM_ENABLED }
  e.body = { ...DEFAULT_ITEM_ENABLED }
  e.caption = { ...DEFAULT_ITEM_ENABLED }
  e.reference = { ...DEFAULT_ITEM_ENABLED }
  e.header = { ...DEFAULT_ITEM_ENABLED }
  e.footer = { ...DEFAULT_ITEM_ENABLED }
  return e
})
```

- [ ] **步骤 2：customizeSettings 调用传入 enabled**

```typescript
await api.customizeSettings(jobId, formatSettings, enabledSettings)
```

在 selectMode 的 auto 模式、manual 模式、submitAnnotations 中三处调用都传入。

- [ ] **步骤 3：resetSettings 同时重置 enabled**

```typescript
const resetSettings = () => {
  setFormatSettings({ ...DEFAULT_FORMAT_SETTINGS })
  // deep clone enabled too
  setEnabledSettings(structuredClone(DEFAULT_ENABLED_SETTINGS))
}
```

- [ ] **步骤 4：TypeScript 编译检查**

运行：`npx tsc --noEmit --pretty`
预期：零错误

---

### 任务 5：FormatSettingsPanel 添加勾选框

**文件：**
- 修改：`frontend/src/components/format/FormatSettingsPanel.tsx`

- [ ] **步骤 1：导入 Checkbox 组件和新类型**

```typescript
import { Checkbox } from "@/components/ui/checkbox"
import type { FormatSettings, FormatSettingItem, FormatSettingsEnabled, FormatSettingItemEnabled } from "@/types"
import { FONT_NAMES, FONT_SIZES, DEFAULT_ENABLED_SETTINGS } from "@/types"
```

- [ ] **步骤 2：扩展 Props**

```typescript
interface Props {
  settings: FormatSettings
  enabled: FormatSettingsEnabled
  onChange: (settings: FormatSettings) => void
  onEnabledChange: (enabled: FormatSettingsEnabled) => void
  onReset: () => void
}
```

- [ ] **步骤 3：添加页面设置勾选框**

在 UnitInput 行中，每个字段前加 Checkbox：
```tsx
<div className="flex items-center gap-1.5">
  <Checkbox
    checked={enabled.page_margin_top}
    onCheckedChange={(v) => onEnabledChange({ ...enabled, page_margin_top: !!v })}
    className="h-3.5 w-3.5"
  />
  <UnitInput label="上边距(cm)" value={settings.page_margin_top} ... />
</div>
```

- [ ] **步骤 4：ItemEditor 增加勾选框参数**

```typescript
function ItemEditor({ item, enabled, onChange, onEnabledChange, showIndent }: {
  item: FormatSettingItem
  enabled: FormatSettingItemEnabled
  onChange: (change: ItemChange) => void
  onEnabledChange: (change: ItemChange) => void
  showIndent?: boolean
})
```

每个字段行改为带 checkbox：
```tsx
<div>
  <div className="flex items-center gap-1">
    <Checkbox checked={enabled.font_name} onCheckedChange={(v) => onEnabledChange({ field: "font_name", value: !!v })} className="h-3 w-3" />
    <Label className="text-[10px] text-muted-foreground">字体</Label>
  </div>
  <Select ...>
```

- [ ] **步骤 5：TypeScript 编译 + Vite 构建**

运行：`npx tsc --noEmit --pretty && npx vite build --logLevel warn`
预期：零错误

---

### 任务 6：端到端验证

- [ ] **步骤 1：确认后端 API 正常**

运行：`curl -s http://localhost:8000/api/health`
预期：`{"status":"ok"}`

- [ ] **步骤 2：确认模板接口仍正常**

运行：`curl -s http://localhost:8000/api/templates/`
预期：返回模板列表含系统默认

- [ ] **步骤 3：前端构建通过**

确认 Vite build 无警告

- [ ] **步骤 4：UI 验证清单**

打开 http://localhost:5173，确认：
1. 格式面板中每个字段左侧有勾选框
2. 默认全部勾选
3. 取消勾选后可正常操作
4. "使用学术规范默认值"按钮同时重置所有勾选框
5. 字体/字号下拉框功能正常（第二步功能保持）
