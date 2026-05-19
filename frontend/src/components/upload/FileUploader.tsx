import { useRef, useState, useEffect, type DragEvent } from "react"
import { Upload } from "lucide-react"
import { cn } from "@/lib/utils"
import { UploadProgress } from "./UploadProgress"
import { useFileUpload } from "@/hooks/useFileUpload"

interface Props {
  onUploaded: (jobId: string, filename: string, fileType: string) => void
}

export function FileUploader({ onUploaded }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const firedRef = useRef(false)
  const { state, progress, job, error, upload, reset } = useFileUpload()

  const handleFile = (file: File) => {
    setSelectedFile(file)
    upload(file)
  }

  const triggerUpload = () => inputRef.current?.click()

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  useEffect(() => {
    if (job && state === "done" && !firedRef.current) {
      firedRef.current = true
      onUploaded(job.id, job.original_filename, job.file_type)
    }
  }, [job, state, onUploaded])

  if (state === "uploading" || state === "done") {
    return (
      <UploadProgress
        progress={progress}
        filename={selectedFile?.name || ""}
        done={state === "done"}
      />
    )
  }

  return (
    <div className="space-y-4">
      <div
        className={cn(
          "border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors",
          dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50",
          error && "border-destructive"
        )}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={triggerUpload}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
          }}
        />
        <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
        <p className="text-lg font-medium mb-1">拖拽论文文件到此处，或点击上传</p>
        <p className="text-sm text-muted-foreground">支持 .pdf 和 .docx 格式，最大 50MB</p>
      </div>
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-3 text-sm text-destructive flex items-center gap-2">
          {error}
          <button onClick={reset} className="ml-auto underline">重试</button>
        </div>
      )}
    </div>
  )
}
