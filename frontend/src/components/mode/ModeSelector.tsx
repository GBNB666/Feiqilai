import { Zap, Edit3 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { FormatMode } from "@/types"

interface Props {
  onSelect: (mode: FormatMode) => void
  disabled?: boolean
}

const modes = [
  {
    id: "auto" as FormatMode,
    title: "一键全自动排版",
    description: "AI自动识别论文结构，按学术规范排版",
    icon: Zap,
    color: "text-amber-500",
    bgColor: "bg-amber-50",
  },
  {
    id: "manual" as FormatMode,
    title: "手动标注结构",
    description: "AI先分析结构，您可校对调整后再排版",
    icon: Edit3,
    color: "text-blue-500",
    bgColor: "bg-blue-50",
  },
]

export function ModeSelector({ onSelect, disabled }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">选择排版模式</h2>
      <div className="grid sm:grid-cols-2 gap-4">
        {modes.map((mode) => (
          <Card
            key={mode.id}
            className={cn(
              "p-6 cursor-pointer transition-all hover:border-primary hover:shadow-md",
              disabled && "opacity-50 pointer-events-none"
            )}
            onClick={() => onSelect(mode.id)}
          >
            <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center mb-3", mode.bgColor)}>
              <mode.icon className={cn("w-5 h-5", mode.color)} />
            </div>
            <h3 className="font-semibold mb-1">{mode.title}</h3>
            <p className="text-sm text-muted-foreground">{mode.description}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}
