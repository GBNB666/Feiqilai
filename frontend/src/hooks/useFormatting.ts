import { useState } from "react"
import { api } from "@/services/api"
import type { FormatJob, FormatMode, PaperStructure, PreviewResponse, FormatSettings, FormatSettingsEnabled, AnalysisWarnings } from "@/types"
import { DEFAULT_FORMAT_SETTINGS, DEFAULT_ENABLED_SETTINGS } from "@/types"

type FormatState = "idle" | "selecting" | "analyzing" | "analyzed" | "annotating" | "formatting" | "done" | "error"

export function useFormatting(jobId: string) {
  const [state, setState] = useState<FormatState>("selecting")
  const [job, setJob] = useState<FormatJob | null>(null)
  const [structure, setStructure] = useState<PaperStructure | null>(null)
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [warnings, setWarnings] = useState<AnalysisWarnings | null>(null)
  const [formatSettings, setFormatSettings] = useState<FormatSettings>({ ...DEFAULT_FORMAT_SETTINGS })
  const [enabledSettings, setEnabledSettings] = useState<FormatSettingsEnabled>(structuredClone(DEFAULT_ENABLED_SETTINGS))
  const [error, setError] = useState("")
  const [step, setStep] = useState<"upload" | "mode" | "settings" | "processing" | "done">("mode")

  const fetchPreview = async (id: string) => {
    try {
      const p = await api.getPreview(id)
      setPreview(p)
    } catch {
      // Preview is optional
    }
  }

  const selectMode = async (mode: FormatMode) => {
    setError("")
    setStep("processing")
    try {
      const j = await api.selectMode(jobId, mode)
      setJob(j)

      if (mode === "auto") {
        setState("analyzing")
        const analyzed = await api.startAnalysis(jobId)
        setJob(analyzed)
        if (analyzed.ai_analysis) {
          try {
            const parsed = JSON.parse(analyzed.ai_analysis)
            if (parsed.structure) {
              setStructure(parsed.structure)
              setWarnings(parsed.warnings || null)
            } else {
              setStructure(parsed)
            }
          } catch {}
        }
        setState("formatting")
        await api.customizeSettings(jobId, formatSettings, enabledSettings)
        const completed = await api.executeFormatting(jobId)
        setJob(completed)
        setState("done")
        setStep("done")
        fetchPreview(jobId)
      } else {
        setState("analyzing")
        const analyzed = await api.startAnalysis(jobId)
        setJob(analyzed)
        if (analyzed.ai_analysis) {
          try {
            const parsed = JSON.parse(analyzed.ai_analysis)
            if (parsed.structure) {
              setStructure(parsed.structure)
              setWarnings(parsed.warnings || null)
            } else {
              setStructure(parsed)
            }
          } catch {}
        }
        setState("analyzed")
        setStep("processing")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "处理失败")
      setState("error")
    }
  }

  const submitAnnotations = async (annotations: string) => {
    setState("annotating")
    try {
      await api.submitAnnotations(jobId, annotations)
      setState("formatting")
      await api.customizeSettings(jobId, formatSettings, enabledSettings)
      const completed = await api.executeFormatting(jobId)
      setJob(completed)
      setState("done")
      setStep("done")
      fetchPreview(jobId)
    } catch (err) {
      setError(err instanceof Error ? err.message : "标注提交失败")
      setState("error")
    }
  }

  const modifySection = async (sectionIndex: number, newContent: string) => {
    await api.modifySection(jobId, sectionIndex, newContent)
    fetchPreview(jobId)
  }

  const resetSettings = () => {
    setFormatSettings({ ...DEFAULT_FORMAT_SETTINGS })
    setEnabledSettings(structuredClone(DEFAULT_ENABLED_SETTINGS))
  }

  return {
    state, job, structure, preview, warnings, formatSettings, enabledSettings, error, step,
    selectMode, submitAnnotations, modifySection,
    setFormatSettings, setEnabledSettings, resetSettings,
  }
}
