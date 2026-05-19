# 格式编辑面板字体/字号下拉选择框

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**目标：** 将 FormatSettingsPanel 中字体和字号的自由文本输入改为下拉选择框，以 Word 为蓝本预置选项。

**架构：** 在 types/index.ts 导出 FONT_NAMES、FONT_SIZES 常量数组，便于复用；FormatSettingsPanel.tsx 的 ItemEditor 中把 font_name 的 `<Input>` 替换为 `<Select>`，把 font_size 的 `<Input type="number">` 替换为 `<Select>`。顶部"重置默认"按钮升级为更大更明确的"使用学术规范默认值"按钮。

**技术栈：** React + TypeScript + shadcn/ui Select

---

### 任务 1：新增字体/字号常量

**文件：**
- 修改：`frontend/src/types/index.ts`

- [ ] **步骤 1：在 DEFAULT_FORMAT_SETTINGS 之前添加两个常量数组**

```typescript
export const FONT_NAMES = ["宋体", "黑体", "仿宋", "楷体", "Times New Roman", "Arial"] as const

export const FONT_SIZES = [
  { label: "初号 (42pt)", value: 42 },
  { label: "小初 (36pt)", value: 36 },
  { label: "一号 (26pt)", value: 26 },
  { label: "小一 (24pt)", value: 24 },
  { label: "二号 (22pt)", value: 22 },
  { label: "小二 (18pt)", value: 18 },
  { label: "三号 (16pt)", value: 16 },
  { label: "小三 (15pt)", value: 15 },
  { label: "四号 (14pt)", value: 14 },
  { label: "小四 (12pt)", value: 12 },
  { label: "五号 (10.5pt)", value: 10.5 },
  { label: "小五 (9pt)", value: 9 },
] as const
```

- [ ] **步骤 2：运行 TypeScript 检查确保常量类型正确**

运行：`npx tsc --noEmit --pretty`
预期：零错误

---

### 任务 2：ItemEditor 字体/字号改为下拉框

**文件：**
- 修改：`frontend/src/components/format/FormatSettingsPanel.tsx`

- [ ] **步骤 1：引入 Select 组件和常量**

文件顶部已有 Select 导入，新增 `FONT_NAMES` 和 `FONT_SIZES` 导入：
```typescript
import { FONT_NAMES, FONT_SIZES } from "@/types"
```

- [ ] **步骤 2：替换字体 Input 为 Select**

将 ItemEditor 中第 112-114 行：
```tsx
<Input value={item.font_name} onChange={(e) => onChange({ field: "font_name", value: e.target.value })} className="h-7 text-xs" />
```

替换为：
```tsx
<Select value={item.font_name} onValueChange={(v) => onChange({ field: "font_name", value: v })}>
  <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
  <SelectContent>
    {FONT_NAMES.map((f) => (
      <SelectItem key={f} value={f}>{f}</SelectItem>
    ))}
  </SelectContent>
</Select>
```

- [ ] **步骤 3：替换字号 Input 为 Select**

将 ItemEditor 中第 115-118 行：
```tsx
<Input type="number" value={item.font_size} onChange={(e) => onChange({ field: "font_size", value: +e.target.value || 0 })} className="h-7 text-xs" />
```

替换为：
```tsx
<Select value={String(item.font_size)} onValueChange={(v) => onChange({ field: "font_size", value: +v })}>
  <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
  <SelectContent>
    {FONT_SIZES.map((s) => (
      <SelectItem key={s.value} value={String(s.value)}>{s.label}</SelectItem>
    ))}
  </SelectContent>
</Select>
```

- [ ] **步骤 4：升级顶部重置按钮**

将第 33-36 行：
```tsx
<Button variant="ghost" size="sm" onClick={onReset} className="h-7 text-xs">
  <RotateCcw className="w-3 h-3 mr-1" />
  重置默认
</Button>
```

替换为：
```tsx
<Button variant="default" size="sm" onClick={onReset} className="h-7 text-xs">
  <RotateCcw className="w-3 h-3 mr-1" />
  使用学术规范默认值
</Button>
```

同时移除顶部不再需要的 `Input` 导入（Select 已导入，Input 仍被 UnitInput 使用，保留）。

- [ ] **步骤 5：TypeScript 编译检查**

运行：`npx tsc --noEmit --pretty`
预期：零错误

---

### 任务 3：Vite 构建验证

- [ ] **步骤 1：生产构建**

运行：`npx vite build --logLevel warn`
预期：构建成功，无错误

- [ ] **步骤 2：功能验证**

打开 http://localhost:5173，确认：
1. 格式面板中字体字段显示为下拉框，包含 6 种字体
2. 字号字段显示为下拉框，包含 12 档中文字号+磅值
3. 点击"使用学术规范默认值"按钮，所有值恢复为系统默认
4. 已有功能（页边距、行距、加粗、对齐等）正常
