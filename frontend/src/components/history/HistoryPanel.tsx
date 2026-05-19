import { Clock, Trash2, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { formatRelativeTime } from "@/hooks/useHistory"
import type { HistoryRecord } from "@/types"

interface Props {
  records: HistoryRecord[]
  onClear: () => void
  onOpen: (jobId: string) => void
}

export function HistoryPanel({ records, onClear, onOpen }: Props) {
  if (records.length === 0) return null

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-sm font-medium">
          <Clock className="w-4 h-4 text-muted-foreground" />
          最近排版记录（24h内）
        </div>
        <Button variant="ghost" size="sm" onClick={onClear} className="h-7 text-xs text-muted-foreground hover:text-red-600">
          <Trash2 className="w-3 h-3 mr-1" />
          清空
        </Button>
      </div>
      <div className="space-y-1">
        {records.map((r, i) => (
          <button
            key={i}
            onClick={() => onOpen(r.jobId)}
            className="w-full flex items-center gap-2 p-2 rounded-lg hover:bg-muted/50 text-left transition-colors"
          >
            <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-sm truncate">{r.filename}</div>
              <div className="text-xs text-muted-foreground">
                {r.mode === "auto" ? "全自动" : "手动"} · {r.templateName || "默认模板"} · {formatRelativeTime(r.timestamp)}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
