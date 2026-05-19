# 预览页段落格式悬停浮窗

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**目标：** 鼠标悬停在预览页段落上时，弹出浮窗显示该段的文字格式信息（字体、字号、行距等）。

**架构：** 新建 `FormatTooltip` 组件；`ResultPreview` 接收 `formatSettings` + `enabledSettings` props，将 content 按行拆分为独立段落，每个段落绑定 onMouseEnter/onMouseLeave；浮窗绝对定位锚定在段落上方。

**技术栈：** React + TypeScript，纯前端，不涉及后端改动。

---

### 任务 1：创建 FormatTooltip 组件

**文件：**
- 创建：`frontend/src/components/result/FormatTooltip.tsx`

- [ ] **步骤 1：编写组件**

根据段落的 level 映射到对应的 formatSetting，显示格式信息。

```tsx
import type { FormatSettingItem, FormatSettingItemEnabled } from "@/types"

interface FormatInfo {
  label: string        // "一级标题" / "正文" / "图注" 等
  settings: FormatSettingItem
  enabled: FormatSettingItemEnabled
}

interface Props {
  info: FormatInfo | null
  anchorRect: DOMRect | null
}

export function FormatTooltip({ info, anchorRect }: Props) {
  if (!info || !anchorRect) return null

  const { settings, enabled, label } = info

  const rows: [string, string | number, boolean][] = [
    ["字体", settings.font_name, enabled.font_name],
    ["字号", `${settings.font_size}pt`, enabled.font_size],
    ["加粗", settings.bold ? "是" : "否", enabled.bold],
    ["对齐", alignLabel(settings.alignment), enabled.alignment],
    ["行距", `${settings.line_spacing}倍`, enabled.line_spacing],
    ["段前距", `${settings.space_before}pt`, enabled.space_before],
    ["段后距", `${settings.space_after}pt`, enabled.space_after],
    ["首行缩进", settings.first_line_indent ? `${settings.first_line_indent}pt` : "无", enabled.first_line_indent],
  ]

  const left = Math.max(0, anchorRect.left)
  const top = Math.max(0, anchorRect.top - 10)

  return (
    <div
      className="fixed z-50 bg-black/85 text-white text-xs rounded-lg px-3 py-2 shadow-xl pointer-events-none"
      style={{ left, top, transform: "translateY(-100%)" }}
    >
      <div className="font-semibold mb-1 border-b border-white/20 pb-1">{label}</div>
      {rows.map(([name, val, en]) => (
        <div key={name as string} className="flex justify-between gap-3">
          <span className="text-white/60">{name}</span>
          <span className={en ? "" : "line-through text-white/40"}>
            {en ? val : "保留原文"}
          </span>
        </div>
      ))}
    </div>
  )
}

function alignLabel(a: string): string {
  const map: Record<string, string> = { left: "左对齐", center: "居中", right: "右对齐", justify: "两端对齐" }
  return map[a] || a || "—"
}
```

- [ ] **步骤 2：TypeScript 编译检查**

运行：`npx tsc --noEmit --pretty`
预期：零错误

---

### 任务 2：更新 ResultPreview 支持段落悬停

**文件：**
- 修改：`frontend/src/components/result/ResultPreview.tsx`

- [ ] **步骤 1：扩展 Props，接收格式设置**

Props 新增：
```typescript
interface Props {
  job: FormatJob
  preview: PreviewResponse | null
  formatSettings?: FormatSettings
  enabledSettings?: FormatSettingsEnabled
  onModifySection: ...
  onBack?: () => void
}
```

- [ ] **步骤 2：添加悬停状态管理**

```typescript
const [tooltipInfo, setTooltipInfo] = useState<FormatInfo | null>(null)
const [tooltipRect, setTooltipRect] = useState<DOMRect | null>(null)
```

- [ ] **步骤 3：编写 getLevelInfo 辅助函数**

```typescript
function getLevelInfo(level: number, settings: FormatSettings, enabled: FormatSettingsEnabled): FormatInfo {
  const map: Record<number, { label: string; key: keyof FormatSettings }> = {
    1: { label: "一级标题", key: "h1" },
    2: { label: "二级标题", key: "h2" },
    3: { label: "三级标题", key: "h3" },
  }
  const m = map[level]
  if (m) return { label: m.label, settings: settings[m.key] as FormatSettingItem, enabled: enabled[m.key] as FormatSettingItemEnabled }
  return { label: "正文", settings: settings.body, enabled: enabled.body }
}
```

- [ ] **步骤 4：将 content 拆分为独立段落，各自绑定悬停事件**

在每个 section 的 content 区域，用 `split("\n")` 拆行，每个段落包在 div 中并绑定 onMouseEnter/onMouseLeave：

```tsx
{s.content && formatSettings && enabledSettings && (
  <div className="text-sm leading-relaxed ...">
    {s.content.split("\n").map((line, pi) => (
      <p
        key={pi}
        className="mb-1"
        onMouseEnter={(e) => {
          const rect = (e.target as HTMLElement).getBoundingClientRect()
          setTooltipInfo(getLevelInfo(s.level, formatSettings, enabledSettings))
          setTooltipRect(rect)
        }}
        onMouseLeave={() => { setTooltipInfo(null); setTooltipRect(null) }}
      >
        {line || " "}
      </p>
    ))}
  </div>
)}
```

标题行同样绑定悬停事件（显示对应层级的标题格式）。

- [ ] **步骤 5：渲染 FormatTooltip**

在组件 return 末尾：
```tsx
<FormatTooltip info={tooltipInfo} anchorRect={tooltipRect} />
```

- [ ] **步骤 6：TypeScript 编译 + Vite 构建**

运行：`npx tsc --noEmit --pretty && npx vite build --logLevel warn`
预期：零错误

---

### 任务 3：ProcessPage 传递格式设置

**文件：**
- 修改：`frontend/src/pages/ProcessPage.tsx`

- [ ] **步骤 1：ResultPreview 新增 props**

```tsx
<ResultPreview
  job={job}
  preview={preview}
  formatSettings={formatSettings}
  enabledSettings={enabledSettings}
  onModifySection={modifySection}
  onBack={() => navigate("/")}
/>
```

---

### 任务 4：端到端验证

- [ ] **步骤 1：构建通过**

运行：`npx tsc --noEmit --pretty && npx vite build`
预期：零错误

- [ ] **步骤 2：UI 验证清单**

1. 鼠标悬停段落标题 → 浮窗显示标题格式（含"一级/二级/三级标题"标签）
2. 鼠标悬停正文 → 浮窗显示正文格式
3. 浮窗显示字体、字号、行距、加粗、对齐、段前段后、首行缩进
4. 取消勾选的字段显示"保留原文"（删除线样式）
5. 鼠标移开浮窗消失
6. 第二步的下拉框、第三步的勾选框功能正常
