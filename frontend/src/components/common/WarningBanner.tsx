import { AlertTriangle, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { AnalysisWarnings } from "@/types"

interface Props {
  warnings: AnalysisWarnings
  onDismiss?: () => void
}

export function WarningBanner({ warnings, onDismiss }: Props) {
  const items: string[] = []
  if (warnings.missing_abstract) items.push("缺少摘要")
  if (warnings.missing_toc) items.push("缺少目录")
  if (warnings.missing_references) items.push("缺少参考文献")
  if (warnings.conflicting_headings.length > 0) items.push(...warnings.conflicting_headings)
  if (warnings.missing_figure_labels.length > 0)
    items.push(`图表缺标注: ${warnings.missing_figure_labels.join(", ")}`)
  if (warnings.missing_table_labels.length > 0)
    items.push(`表格缺标注: ${warnings.missing_table_labels.join(", ")}`)

  if (items.length === 0) return null

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-start gap-2">
      <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-amber-800">格式警告</span>
          {items.map((item, i) => (
            <Badge key={i} variant="outline" className="text-xs border-amber-300 text-amber-700 bg-amber-50">
              {item}
            </Badge>
          ))}
        </div>
        <p className="text-xs text-amber-600 mt-1">不影响排版，建议检查原文</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-amber-500 hover:text-amber-700">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}
