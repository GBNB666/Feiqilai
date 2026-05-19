import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronDown, ChevronRight, RotateCcw } from "lucide-react"
import type { FormatSettings, FormatSettingItem, FormatSettingsEnabled, FormatSettingItemEnabled } from "@/types"
import { FONT_NAMES, FONT_SIZES } from "@/types"

interface Props {
  settings: FormatSettings
  enabled: FormatSettingsEnabled
  onChange: (settings: FormatSettings) => void
  onEnabledChange: (enabled: FormatSettingsEnabled) => void
  onReset: () => void
}

export function FormatSettingsPanel({ settings, enabled, onChange, onEnabledChange, onReset }: Props) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ page: true })

  const toggle = (key: string) => setExpanded((p) => ({ ...p, [key]: !p[key] }))

  const update = (key: string, field: string, value: any) => {
    const next = { ...settings, [key]: { ...(settings as any)[key], [field]: value } }
    onChange(next)
  }

  const updateEnabled = (key: string, field: string, value: boolean) => {
    const next = { ...enabled, [key]: { ...(enabled as any)[key], [field]: value } }
    onEnabledChange(next)
  }

  const updatePage = (field: string, value: number) => {
    onChange({ ...settings, [field]: value })
  }

  const updatePageEnabled = (field: string, value: boolean) => {
    onEnabledChange({ ...enabled, [field]: value })
  }

  return (
    <div className="space-y-2 text-sm">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm">格式设置</h3>
        <Button variant="default" size="sm" onClick={onReset} className="h-7 text-xs">
          <RotateCcw className="w-3 h-3 mr-1" />
          使用学术规范默认值
        </Button>
      </div>

      {/* Page Settings */}
      <Section title="页面设置" expanded={expanded.page} onToggle={() => toggle("page")}>
        <div className="grid grid-cols-2 gap-2">
          <CheckUnit label="上边距(cm)" value={settings.page_margin_top} checked={enabled.page_margin_top} onChange={(v) => updatePage("page_margin_top", v)} onCheckedChange={(v) => updatePageEnabled("page_margin_top", v)} />
          <CheckUnit label="下边距(cm)" value={settings.page_margin_bottom} checked={enabled.page_margin_bottom} onChange={(v) => updatePage("page_margin_bottom", v)} onCheckedChange={(v) => updatePageEnabled("page_margin_bottom", v)} />
          <CheckUnit label="左边距(cm)" value={settings.page_margin_left} checked={enabled.page_margin_left} onChange={(v) => updatePage("page_margin_left", v)} onCheckedChange={(v) => updatePageEnabled("page_margin_left", v)} />
          <CheckUnit label="右边距(cm)" value={settings.page_margin_right} checked={enabled.page_margin_right} onChange={(v) => updatePage("page_margin_right", v)} onCheckedChange={(v) => updatePageEnabled("page_margin_right", v)} />
          <CheckUnit label="页眉距(cm)" value={settings.header_distance} checked={enabled.header_distance} onChange={(v) => updatePage("header_distance", v)} onCheckedChange={(v) => updatePageEnabled("header_distance", v)} />
          <CheckUnit label="页脚距(cm)" value={settings.footer_distance} checked={enabled.footer_distance} onChange={(v) => updatePage("footer_distance", v)} onCheckedChange={(v) => updatePageEnabled("footer_distance", v)} />
        </div>
      </Section>

      {/* Heading 1 */}
      <Section title="一级标题" expanded={expanded.h1} onToggle={() => toggle("h1")}>
        <ItemEditor item={settings.h1} enabled={enabled.h1} onChange={(v) => update("h1", v.field, v.value)} onEnabledChange={(v) => updateEnabled("h1", v.field, v.value)} />
      </Section>

      {/* Heading 2 */}
      <Section title="二级标题" expanded={expanded.h2} onToggle={() => toggle("h2")}>
        <ItemEditor item={settings.h2} enabled={enabled.h2} onChange={(v) => update("h2", v.field, v.value)} onEnabledChange={(v) => updateEnabled("h2", v.field, v.value)} />
      </Section>

      {/* Heading 3 */}
      <Section title="三级标题" expanded={expanded.h3} onToggle={() => toggle("h3")}>
        <ItemEditor item={settings.h3} enabled={enabled.h3} onChange={(v) => update("h3", v.field, v.value)} onEnabledChange={(v) => updateEnabled("h3", v.field, v.value)} />
      </Section>

      {/* Body */}
      <Section title="正文" expanded={expanded.body} onToggle={() => toggle("body")}>
        <ItemEditor item={settings.body} enabled={enabled.body} onChange={(v) => update("body", v.field, v.value)} onEnabledChange={(v) => updateEnabled("body", v.field, v.value)} showIndent />
      </Section>

      {/* Caption */}
      <Section title="图注/表注" expanded={expanded.caption} onToggle={() => toggle("caption")}>
        <ItemEditor item={settings.caption} enabled={enabled.caption} onChange={(v) => update("caption", v.field, v.value)} onEnabledChange={(v) => updateEnabled("caption", v.field, v.value)} />
      </Section>

      {/* Reference */}
      <Section title="参考文献" expanded={expanded.ref} onToggle={() => toggle("ref")}>
        <ItemEditor item={settings.reference} enabled={enabled.reference} onChange={(v) => update("reference", v.field, v.value)} onEnabledChange={(v) => updateEnabled("reference", v.field, v.value)} />
      </Section>

      {/* TOC Settings */}
      <Section title="目录设置" expanded={expanded.toc} onToggle={() => toggle("toc")}>
        <div className="space-y-2">
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

      {/* Header */}
      <Section title="页眉" expanded={expanded.header} onToggle={() => toggle("header")}>
        <ItemEditor item={settings.header} enabled={enabled.header} onChange={(v) => update("header", v.field, v.value)} onEnabledChange={(v) => updateEnabled("header", v.field, v.value)} />
      </Section>

      {/* Footer */}
      <Section title="页脚" expanded={expanded.footer} onToggle={() => toggle("footer")}>
        <ItemEditor item={settings.footer} enabled={enabled.footer} onChange={(v) => update("footer", v.field, v.value)} onEnabledChange={(v) => updateEnabled("footer", v.field, v.value)} />
      </Section>
    </div>
  )
}

function Section({ title, expanded, onToggle, children }: { title: string; expanded: boolean; onToggle: () => void; children: React.ReactNode }) {
  return (
    <div className="border rounded-lg">
      <button onClick={onToggle} className="w-full flex items-center justify-between px-3 py-2 hover:bg-muted/50 rounded-lg text-xs font-medium">
        {title}
        {expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>
      {expanded && <div className="px-3 pb-2 space-y-1.5">{children}</div>}
    </div>
  )
}

type ItemChange = { field: string; value: any }

function ItemEditor({ item, enabled, onChange, onEnabledChange, showIndent }: {
  item: FormatSettingItem
  enabled: FormatSettingItemEnabled
  onChange: (change: ItemChange) => void
  onEnabledChange: (change: ItemChange) => void
  showIndent?: boolean
}) {
  return (
    <div className="grid grid-cols-2 gap-1.5">
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.font_name} onCheckedChange={(v) => onEnabledChange({ field: "font_name", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">字体</Label>
        </div>
        <Select value={item.font_name} onValueChange={(v) => onChange({ field: "font_name", value: v })}>
          <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
          <SelectContent>
            {FONT_NAMES.map((f) => (
              <SelectItem key={f} value={f}>{f}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.font_size} onCheckedChange={(v) => onEnabledChange({ field: "font_size", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">字号</Label>
        </div>
        <Select value={String(item.font_size)} onValueChange={(v) => onChange({ field: "font_size", value: +v })}>
          <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
          <SelectContent>
            {FONT_SIZES.map((s) => (
              <SelectItem key={s.value} value={String(s.value)}>{s.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.bold} onCheckedChange={(v) => onEnabledChange({ field: "bold", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">加粗</Label>
        </div>
        <Select value={item.bold ? "yes" : "no"} onValueChange={(v) => onChange({ field: "bold", value: v === "yes" })}>
          <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value="yes">是</SelectItem><SelectItem value="no">否</SelectItem></SelectContent>
        </Select>
      </div>
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.alignment} onCheckedChange={(v) => onEnabledChange({ field: "alignment", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">对齐</Label>
        </div>
        <Select value={item.alignment} onValueChange={(v) => onChange({ field: "alignment", value: v })}>
          <SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="left">左对齐</SelectItem>
            <SelectItem value="center">居中</SelectItem>
            <SelectItem value="right">右对齐</SelectItem>
            <SelectItem value="justify">两端对齐</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.line_spacing} onCheckedChange={(v) => onEnabledChange({ field: "line_spacing", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">行距</Label>
        </div>
        <Input type="number" step="0.25" value={item.line_spacing} onChange={(e) => onChange({ field: "line_spacing", value: +e.target.value || 0 })} className="h-7 text-xs" />
      </div>
      {showIndent && (
        <div>
          <div className="flex items-center gap-1">
            <Checkbox checked={enabled.first_line_indent} onCheckedChange={(v) => onEnabledChange({ field: "first_line_indent", value: !!v })} className="h-3 w-3" />
            <Label className="text-[10px] text-muted-foreground">首行缩进(pt)</Label>
          </div>
          <Input type="number" value={item.first_line_indent} onChange={(e) => onChange({ field: "first_line_indent", value: +e.target.value || 0 })} className="h-7 text-xs" />
        </div>
      )}
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.space_before} onCheckedChange={(v) => onEnabledChange({ field: "space_before", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">段前距(pt)</Label>
        </div>
        <Input type="number" value={item.space_before} onChange={(e) => onChange({ field: "space_before", value: +e.target.value || 0 })} className="h-7 text-xs" />
      </div>
      <div>
        <div className="flex items-center gap-1">
          <Checkbox checked={enabled.space_after} onCheckedChange={(v) => onEnabledChange({ field: "space_after", value: !!v })} className="h-3 w-3" />
          <Label className="text-[10px] text-muted-foreground">段后距(pt)</Label>
        </div>
        <Input type="number" value={item.space_after} onChange={(e) => onChange({ field: "space_after", value: +e.target.value || 0 })} className="h-7 text-xs" />
      </div>
    </div>
  )
}

function CheckUnit({ label, value, checked, onChange, onCheckedChange }: {
  label: string; value: number; checked: boolean;
  onChange: (v: number) => void; onCheckedChange: (v: boolean) => void;
}) {
  return (
    <div>
      <div className="flex items-center gap-1">
        <Checkbox checked={checked} onCheckedChange={(v) => onCheckedChange(!!v)} className="h-3 w-3" />
        <Label className="text-[10px] text-muted-foreground">{label}</Label>
      </div>
      <Input type="number" step="0.01" value={value} onChange={(e) => onChange(+e.target.value || 0)} className="h-7 text-xs" />
    </div>
  )
}
