import { useState, useEffect, useCallback } from "react"
import { api } from "@/services/api"
import type { TemplateInfo } from "@/types"

export function useTemplate() {
  const [templates, setTemplates] = useState<TemplateInfo[]>([])
  const [loading, setLoading] = useState(false)

  const fetchTemplates = useCallback(async () => {
    setLoading(true)
    try {
      const list = await api.listTemplates()
      setTemplates(list)
    } catch {
      // Server may not be running yet
    }
    setLoading(false)
  }, [])

  useEffect(() => { fetchTemplates() }, [fetchTemplates])

  const saveTemplate = useCallback(async (name: string, settings: any) => {
    const t = await api.saveTemplate(name, settings)
    setTemplates((prev) => [t, ...prev])
    return t
  }, [])

  const deleteTemplate = useCallback(async (id: number) => {
    await api.deleteTemplate(id)
    setTemplates((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return { templates, loading, saveTemplate, deleteTemplate, refresh: fetchTemplates }
}
