import { useEffect, useState } from "react"
import type { FormatSettingItem, FormatSettingItemEnabled } from "@/types"

export interface FormatInfo {
  label: string
  settings: FormatSettingItem
  enabled: FormatSettingItemEnabled
}

interface Props {
  info: FormatInfo | null
  anchorRect: DOMRect | null
}

function alignLabel(a: string): string {
  const map: Record<string, string> = { left: "左对齐", center: "居中", right: "右对齐", justify: "两端对齐" }
  return map[a] || a || "—"
}

export function FormatTooltip({ info, anchorRect }: Props) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    setVisible(true)
  }, [info, anchorRect])

  useEffect(() => {
    const handleScroll = () => setVisible(false)
    window.addEventListener("scroll", handleScroll, true)
    return () => window.removeEventListener("scroll", handleScroll, true)
  }, [])

  if (!info || !anchorRect || !visible) return null

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
