import { useState, useCallback } from "react"
import type { FormatJob } from "@/types"

type UploadState = "idle" | "uploading" | "done" | "error"

export function useFileUpload() {
  const [state, setState] = useState<UploadState>("idle")
  const [progress, setProgress] = useState(0)
  const [job, setJob] = useState<FormatJob | null>(null)
  const [error, setError] = useState("")

  const upload = useCallback(async (file: File) => {
    setState("uploading")
    setProgress(0)
    setError("")

    const formData = new FormData()
    formData.append("file", file)

    const xhr = new XMLHttpRequest()

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100)
        setProgress(pct)
      }
    })

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        const result: FormatJob = JSON.parse(xhr.responseText)
        setProgress(100)
        setJob(result)
        setState("done")
      } else {
        let message = `上传失败 (${xhr.status})`
        try {
          const err = JSON.parse(xhr.responseText)
          message = err.detail || message
        } catch {}
        setError(message)
        setState("error")
      }
    })

    xhr.addEventListener("error", () => {
      setError("网络错误，请检查连接")
      setState("error")
    })

    xhr.open("POST", "/api/upload")
    xhr.send(formData)
  }, [])

  const reset = useCallback(() => {
    setState("idle")
    setProgress(0)
    setJob(null)
    setError("")
  }, [])

  return { state, progress, job, error, upload, reset }
}
