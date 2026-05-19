import type { FormatJob, PreviewResponse, FormatSettings, FormatSettingsEnabled, TemplateInfo } from "@/types"

const BASE = "/api"

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  upload: async (file: File): Promise<FormatJob> => {
    const formData = new FormData()
    formData.append("file", file)
    const res = await fetch(`${BASE}/upload`, { method: "POST", body: formData })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  },

  selectMode: (jobId: string, mode: string) =>
    request<FormatJob>("/format/select-mode", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, format_mode: mode }),
    }),

  startAnalysis: (jobId: string) =>
    request<FormatJob>(`/format/analyze?job_id=${jobId}`, { method: "POST" }),

  submitAnnotations: (jobId: string, annotations: string) =>
    request<FormatJob>("/format/annotate", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, annotations }),
    }),

  customizeSettings: (jobId: string, settings: FormatSettings, enabled?: FormatSettingsEnabled) =>
    request<FormatJob>("/format/customize", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, settings, enabled }),
    }),

  executeFormatting: (jobId: string) =>
    request<FormatJob>(`/format/execute?job_id=${jobId}`, { method: "POST" }),

  modifySection: (jobId: string, sectionIndex: number, newContent: string) =>
    request<FormatJob>(`/format/modify-section/${jobId}`, {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, section_index: sectionIndex, new_content: newContent }),
    }),

  getJobStatus: (jobId: string) =>
    request<FormatJob>(`/format/job/${jobId}`),

  getPreview: (jobId: string) =>
    request<PreviewResponse>(`/preview/${jobId}`),

  // Templates
  saveTemplate: (name: string, settings: FormatSettings) =>
    request<TemplateInfo>("/templates/save", {
      method: "POST",
      body: JSON.stringify({ name, settings }),
    }),

  listTemplates: () =>
    request<TemplateInfo[]>("/templates/"),

  getTemplate: (id: number) =>
    request<TemplateInfo>(`/templates/${id}`),

  deleteTemplate: (id: number) =>
    request<{ status: string }>(`/templates/${id}`, { method: "DELETE" }),
}

export function getDownloadUrl(jobId: string) {
  return `${BASE}/download/${jobId}`
}
