import { useState } from "react"
import { api } from "@/services/api"
import type { FormatJob } from "@/types"

type UploadState = "idle" | "uploading" | "done" | "error"

export function useFileUpload() {
  const [state, setState] = useState<UploadState>("idle")
  const [progress, setProgress] = useState(0)
  const [job, setJob] = useState<FormatJob | null>(null)
  const [error, setError] = useState("")

  const upload = async (file: File) => {
    setState("uploading")
    setProgress(0)
    setError("")

    const progressInterval = setInterval(() => {
      setProgress((p) => Math.min(p + 15, 85))
    }, 200)

    try {
      const result = await api.upload(file)
      clearInterval(progressInterval)
      setProgress(100)
      setJob(result)
      setState("done")
    } catch (err) {
      clearInterval(progressInterval)
      setError(err instanceof Error ? err.message : "上传失败")
      setState("error")
    }
  }

  const reset = () => {
    setState("idle")
    setProgress(0)
    setJob(null)
    setError("")
  }

  return { state, progress, job, error, upload, reset }
}
