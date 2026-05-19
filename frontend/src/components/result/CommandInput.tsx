import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronLeft, ChevronRight, Pencil } from "lucide-react"

interface Props {
  sectionCount: number
  currentIndex: number
  onNavigate: (index: number) => void
  onSubmit: (sectionIndex: number, newContent: string) => Promise<void>
}

export function CommandInput({ sectionCount, currentIndex, onNavigate, onSubmit }: Props) {
  const [sectionNum, setSectionNum] = useState(String(currentIndex + 1))
  const [content, setContent] = useState("")
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    setSectionNum(String(currentIndex + 1))
  }, [currentIndex])

  useEffect(() => {
    if (status !== "idle") {
      const timer = setTimeout(() => setStatus("idle"), 2000)
      return () => clearTimeout(timer)
    }
  }, [status])

  const goPrev = () => onNavigate(Math.max(0, currentIndex - 1))
  const goNext = () => onNavigate(Math.min(sectionCount - 1, currentIndex + 1))

  const handleSubmit = async () => {
    const idx = parseInt(sectionNum) - 1
    if (isNaN(idx) || idx < 0 || idx >= sectionCount) {
      setStatus("err")
      return
    }
    if (!content.trim()) {
      setStatus("err")
      return
    }
    setStatus("loading")
    try {
      await onSubmit(idx, content.trim())
      setStatus("ok")
      setContent("")
    } catch {
      setStatus("err")
    }
  }

  return (
    <div className="border rounded-xl p-4 bg-card space-y-3">
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button onClick={goPrev} disabled={currentIndex === 0} variant="ghost" size="sm">
          <ChevronLeft className="w-4 h-4 mr-1" />上一节
        </Button>
        <span className="text-sm font-medium tabular-nums">
          第 {currentIndex + 1} / {sectionCount} 节
        </span>
        <Button onClick={goNext} disabled={currentIndex >= sectionCount - 1} variant="ghost" size="sm">
          下一节<ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>

      {/* Edit area */}
      <div className="flex items-start gap-2">
        <div className="shrink-0 flex items-center gap-1 pt-1.5">
          <span className="text-xs text-muted-foreground">第</span>
          <Input
            value={sectionNum}
            onChange={(e) => setSectionNum(e.target.value)}
            className="w-14 h-8 text-center text-sm"
            placeholder="N"
          />
          <span className="text-xs text-muted-foreground">节</span>
        </div>

        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.ctrlKey) handleSubmit()
            }}
            placeholder=""
            rows={3}
            className="w-full text-sm rounded-md border bg-transparent px-3 py-2 resize-y min-h-[72px] relative z-10"
            disabled={status === "loading"}
          />
          {!content && (
            <div className="absolute inset-0 px-3 py-2 pointer-events-none z-0 select-none">
              <p className="text-xs text-muted-foreground/35 leading-relaxed">
                输入该节的新正文内容，修改后点击确定，系统将重新排版该章节
              </p>
              <p className="text-[10px] text-muted-foreground/20 mt-0.5">
                保留原文可留空跳过 · Ctrl+Enter 快捷提交
              </p>
            </div>
          )}
        </div>

        <Button
          size="sm"
          onClick={handleSubmit}
          disabled={status === "loading" || !content.trim()}
          className="shrink-0 mt-1.5"
        >
          {status === "loading" ? (
            <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Pencil className="w-4 h-4 mr-1" />
          )}
          {status === "loading" ? "排版中" : "修改"}
        </Button>
      </div>

      {status === "ok" && (
        <p className="text-xs text-green-600">第 {sectionNum} 节修改已提交，重新排版完成</p>
      )}
      {status === "err" && (
        <p className="text-xs text-red-500">节号无效或内容为空，请检查后重试</p>
      )}
    </div>
  )
}
