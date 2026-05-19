import { useState, useRef, useEffect } from "react"
import { FileText, ChevronLeft, ChevronRight, Download, BookOpen, Table, Image } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CommandInput } from "./CommandInput"
import { StepNavigation } from "@/components/navigation/StepNavigation"
import { FormatTooltip } from "./FormatTooltip"
import type { FormatInfo } from "./FormatTooltip"
import { getDownloadUrl } from "@/services/api"
import type { FormatJob, PreviewResponse, FormatSettings, FormatSettingsEnabled, FormatSettingItem, FormatSettingItemEnabled, ContentMarker } from "@/types"

interface Props {
  job: FormatJob
  preview: PreviewResponse | null
  formatSettings?: FormatSettings
  enabledSettings?: FormatSettingsEnabled
  onModifySection: (sectionIndex: number, newContent: string) => Promise<void>
  onBack?: () => void
}

const LEVEL_LABELS: Record<number, string> = { 1: "一级标题", 2: "二级标题", 3: "三级标题", 0: "", [-1]: "目录" }

type SettingsKey = "h1" | "h2" | "h3" | "body" | "toc_title"

function getLevelInfo(level: number, settings: FormatSettings, enabled: FormatSettingsEnabled): FormatInfo {
  const map: Record<number, { label: string; key: SettingsKey }> = {
    1: { label: "一级标题", key: "h1" },
    2: { label: "二级标题", key: "h2" },
    3: { label: "三级标题", key: "h3" },
    [-1]: { label: "目录标题", key: "toc_title" },
  }
  const m = map[level]
  if (m) return { label: m.label, settings: settings[m.key] as FormatSettingItem, enabled: enabled[m.key] as FormatSettingItemEnabled }
  return { label: "正文", settings: settings.body, enabled: enabled.body }
}

function PlaceholderBlock({ marker }: { marker: ContentMarker }) {
  const Icon = marker.type === "table" ? Table : Image
  return (
    <div className="border-2 border-dashed border-muted-foreground/30 rounded-lg p-4 my-3 flex items-center gap-3 bg-muted/10">
      <Icon className="w-8 h-8 text-muted-foreground/50 shrink-0" />
      <div>
        <p className="text-sm font-medium text-muted-foreground">
          {marker.type === "table" ? "表格" : "图片"}
        </p>
        <p className="text-xs text-muted-foreground/60">{marker.description}</p>
        <p className="text-[10px] text-muted-foreground/40 mt-0.5">
          此元素受保护，排版时原样保留
        </p>
      </div>
    </div>
  )
}

export function ResultPreview({ job, preview, formatSettings, enabledSettings, onModifySection, onBack }: Props) {
  const [currentIdx, setCurrentIdx] = useState(0)
  const [tooltipInfo, setTooltipInfo] = useState<FormatInfo | null>(null)
  const [tooltipRect, setTooltipRect] = useState<DOMRect | null>(null)
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([])

  const sections = preview?.sections ?? []
  const total = sections.length

  useEffect(() => {
    sectionRefs.current = sectionRefs.current.slice(0, total)
  }, [total])

  const goPrev = () => setCurrentIdx((i) => Math.max(0, i - 1))
  const goNext = () => setCurrentIdx((i) => Math.min(total - 1, i + 1))

  useEffect(() => {
    const el = sectionRefs.current[currentIdx]
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" })
  }, [currentIdx])

  const handleParaHover = (e: React.MouseEvent, sectionLevel: number) => {
    if (!formatSettings || !enabledSettings) return
    const rect = (e.target as HTMLElement).getBoundingClientRect()
    setTooltipInfo(getLevelInfo(sectionLevel, formatSettings, enabledSettings))
    setTooltipRect(rect)
  }

  const handleParaLeave = () => {
    setTooltipInfo(null)
    setTooltipRect(null)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {/* Navigation */}
      <StepNavigation onBack={onBack} backLabel="返回修改格式" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold">排版结果预览</h2>
          <Badge variant="secondary" className="ml-1">共 {total} 节</Badge>
        </div>
        <a href={getDownloadUrl(job.id)} download={`formatted_${job.original_filename}`}>
          <Button size="sm" variant="outline">
            <Download className="w-4 h-4 mr-1" />下载
          </Button>
        </a>
      </div>

      {/* Section navigation — top (always visible) */}
      {total > 0 && (
        <div className="flex items-center justify-between bg-muted/40 rounded-lg px-4 py-3">
          <Button onClick={goPrev} disabled={currentIdx === 0} variant="ghost" size="sm">
            <ChevronLeft className="w-5 h-5 mr-1" />上一节
          </Button>
          <span className="text-sm font-medium tabular-nums">第 {currentIdx + 1} / {total} 节</span>
          <Button onClick={goNext} disabled={currentIdx >= total - 1} variant="ghost" size="sm">
            下一节<ChevronRight className="w-5 h-5 ml-1" />
          </Button>
        </div>
      )}

      {/* Content area */}
      {total > 0 ? (
        <Card className="border shadow-sm">
          <CardHeader className="pb-2 border-b bg-muted/30">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{preview?.title || job.original_filename}</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="pt-4 pb-2 max-h-[50vh] overflow-y-auto">
            <div className="space-y-6">
              {sections.map((s, i) => {
                const isToc = s.level === -1
                return (
                  <div
                    key={i}
                    ref={(el) => { sectionRefs.current[i] = el }}
                    className={`border rounded-lg p-4 transition-colors ${
                      i === currentIdx ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-border"
                    }`}
                  >
                    {/* Section header */}
                    {isToc ? (
                      <div className="text-center mb-3">
                        <Badge variant="outline" className="text-xs mb-1">目录</Badge>
                        <h3
                          className="text-base font-bold"
                          onMouseEnter={(e) => handleParaHover(e, -1)}
                          onMouseLeave={handleParaLeave}
                        >{s.title}</h3>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant={s.level === 1 ? "default" : s.level === 2 ? "secondary" : "outline"} className="text-xs">
                          {LEVEL_LABELS[s.level] || `L${s.level}`}
                        </Badge>
                        <h3
                          className={
                            s.level === 1 ? "text-base font-bold text-center w-full" :
                            s.level === 2 ? "text-sm font-bold" : "text-sm font-semibold"
                          }
                          onMouseEnter={(e) => handleParaHover(e, s.level)}
                          onMouseLeave={handleParaLeave}
                        >{s.title}</h3>
                      </div>
                    )}

                    {/* Section content */}
                    {s.content && s.content.length > 0 && (
                      <div className="text-sm leading-relaxed whitespace-pre-wrap text-muted-foreground font-[serif]">
                        {s.content.map((line, pi) => (
                          <p
                            key={pi}
                            className="mb-1"
                            onMouseEnter={isToc ? undefined : (e) => handleParaHover(e, s.level)}
                            onMouseLeave={isToc ? undefined : handleParaLeave}
                          >
                            {line || " "}
                          </p>
                        ))}
                      </div>
                    )}

                    {/* Markers (tables/images) */}
                    {s.markers && s.markers.length > 0 && (
                      <div className="mt-2">
                        {s.markers.map((m) => (
                          <PlaceholderBlock key={`m-${m.type}-${m.index}`} marker={m} />
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center space-y-2 py-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <FileText className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-xl font-semibold">排版完成</h2>
          <p className="text-muted-foreground">{job.original_filename} 已按学术规范排版完成</p>
        </div>
      )}

      {/* Command modification */}
      <CommandInput
        sectionCount={total}
        currentIndex={currentIdx}
        onNavigate={setCurrentIdx}
        onSubmit={onModifySection}
      />

      {/* Format tooltip */}
      <FormatTooltip info={tooltipInfo} anchorRect={tooltipRect} />
    </div>
  )
}
