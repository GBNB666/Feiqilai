import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"

interface Props {
  sectionCount: number
  onSubmit: (sectionIndex: number, newContent: string) => Promise<void>
}

export function CommandInput({ sectionCount, onSubmit }: Props) {
  const [value, setValue] = useState("")
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle")

  const handleSubmit = async () => {
    const match = value.match(/第(\d+)节\s*正文改为(.+)/)
    if (!match) {
      setStatus("err")
      setTimeout(() => setStatus("idle"), 2000)
      return
    }
    const idx = parseInt(match[1]) - 1
    if (idx < 0 || idx >= sectionCount) {
      setStatus("err")
      setTimeout(() => setStatus("idle"), 2000)
      return
    }
    setStatus("loading")
    try {
      await onSubmit(idx, match[2])
      setStatus("ok")
      setValue("")
      setTimeout(() => setStatus("idle"), 2000)
    } catch {
      setStatus("err")
      setTimeout(() => setStatus("idle"), 2000)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        placeholder={`第X节 正文改为...（共${sectionCount}节）`}
        className="flex-1 text-sm"
        disabled={status === "loading"}
      />
      <Button size="sm" onClick={handleSubmit} disabled={status === "loading"}>
        <Send className="w-4 h-4 mr-1" />
        确定
      </Button>
      {status === "ok" && <span className="text-xs text-green-600">已修改</span>}
      {status === "err" && <span className="text-xs text-red-500">格式错误</span>}
    </div>
  )
}
