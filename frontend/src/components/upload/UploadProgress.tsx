import { CheckCircle2, FileText } from "lucide-react"

interface Props {
  progress: number
  filename: string
  done: boolean
}

export function UploadProgress({ progress, filename, done }: Props) {
  return (
    <div className="border rounded-xl p-6 space-y-4">
      <div className="flex items-center gap-3">
        <FileText className="w-8 h-8 text-primary" />
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{filename}</p>
          <p className="text-sm text-muted-foreground">
            {done ? "上传完成" : `上传中 ${progress}%`}
          </p>
        </div>
        {done && <CheckCircle2 className="w-6 h-6 text-green-500" />}
      </div>
      {!done && (
        <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}
