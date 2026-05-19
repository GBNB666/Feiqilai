import { useParams, useNavigate } from "react-router-dom"
import { ModeSelector } from "@/components/mode/ModeSelector"
import { AnnotationPanel } from "@/components/annotate/AnnotationPanel"
import { ResultPreview } from "@/components/result/ResultPreview"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { WarningBanner } from "@/components/common/WarningBanner"
import { FormatSettingsPanel } from "@/components/format/FormatSettingsPanel"
import { TemplateManager } from "@/components/template/TemplateManager"
import { StepNavigation } from "@/components/navigation/StepNavigation"
import { useFormatting } from "@/hooks/useFormatting"
import { useTemplate } from "@/hooks/useTemplate"
import type { FormatMode, PaperStructure, FormatSettings } from "@/types"

export function ProcessPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const {
    state, job, structure, preview, warnings, formatSettings, enabledSettings, error,
    selectMode, submitAnnotations, modifySection,
    setFormatSettings, setEnabledSettings, resetSettings,
  } = useFormatting(jobId || "")
  const { templates, saveTemplate, deleteTemplate } = useTemplate()

  const handleModeSelect = (mode: FormatMode) => {
    selectMode(mode)
  }

  if (state === "error") return <ErrorAlert message={error} />
  if (state === "analyzing" || state === "formatting") {
    return <LoadingSpinner text={state === "analyzing" ? "AI正在分析论文结构..." : "正在排版中..."} />
  }
  if (state === "done" && job) {
    return (
      <ResultPreview
        job={job}
        preview={preview}
        formatSettings={formatSettings}
        enabledSettings={enabledSettings}
        onModifySection={modifySection}
        onBack={() => navigate("/")}
      />
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex gap-6">
        {/* Left: Format settings panel (always visible during setup) */}
        <div className="w-64 shrink-0 hidden lg:block">
          <div className="sticky top-24 border rounded-xl p-3 bg-muted/10 max-h-[80vh] overflow-y-auto space-y-3">
            <FormatSettingsPanel
              settings={formatSettings}
              enabled={enabledSettings}
              onChange={setFormatSettings}
              onEnabledChange={setEnabledSettings}
              onReset={resetSettings}
            />
            <TemplateManager
              templates={templates}
              currentSettings={formatSettings}
              onSave={async (name) => { await saveTemplate(name, formatSettings) }}
              onLoad={(s: FormatSettings) => setFormatSettings(s)}
              onDelete={async (id) => { await deleteTemplate(id) }}
            />
          </div>
        </div>

        {/* Right: Main flow */}
        <div className="flex-1 space-y-6">
          <StepNavigation
            onBack={() => navigate("/")}
            backLabel="返回首页"
          />

          {/* Mobile format settings toggle */}
          <div className="lg:hidden">
            <details className="border rounded-lg p-3">
              <summary className="text-sm font-medium cursor-pointer">格式设置</summary>
              <div className="mt-2 space-y-3">
                <FormatSettingsPanel
                  settings={formatSettings}
                  enabled={enabledSettings}
                  onChange={setFormatSettings}
                  onEnabledChange={setEnabledSettings}
                  onReset={resetSettings}
                />
                <TemplateManager
                  templates={templates}
                  currentSettings={formatSettings}
                  onSave={async (name) => { await saveTemplate(name, formatSettings) }}
                  onLoad={(s: FormatSettings) => setFormatSettings(s)}
                  onDelete={async (id) => { await deleteTemplate(id) }}
                />
              </div>
            </details>
          </div>

          {/* Warnings */}
          {warnings && <WarningBanner warnings={warnings} />}

          {/* Mode selector */}
          {state === "selecting" && <ModeSelector onSelect={handleModeSelect} />}

          {/* Annotation panel for manual mode */}
          {state === "analyzed" && structure && (
            <AnnotationPanel structure={structure as PaperStructure} onSubmit={submitAnnotations} />
          )}

          {state === "idle" && <LoadingSpinner text="加载中..." />}
        </div>
      </div>
    </div>
  )
}
