import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface Props {
  text?: string
  className?: string
}

export function LoadingSpinner({ text = "处理中...", className }: Props) {
  return (
    <div className={cn("flex flex-col items-center gap-3 py-12", className)}>
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
      <p className="text-muted-foreground text-sm">{text}</p>
    </div>
  )
}
