import { AlertCircle } from "lucide-react"

interface Props {
  message: string
  onRetry?: () => void
}

export function ErrorAlert({ message, onRetry }: Props) {
  return (
    <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4 flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm text-destructive font-medium">出错了</p>
        <p className="text-sm text-destructive/80 mt-1">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-sm text-destructive underline mt-2 hover:no-underline"
          >
            重试
          </button>
        )}
      </div>
    </div>
  )
}
