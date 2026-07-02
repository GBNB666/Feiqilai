const BASE = "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export function uploadFile(file: File, onProgress?: (pct: number) => void): Promise<JobResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BASE}/upload`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          const body = JSON.parse(xhr.responseText);
          reject(new Error(body.detail || "Upload failed"));
        } catch {
          reject(new Error("Upload failed"));
        }
      }
    };

    xhr.onerror = () => reject(new Error("Network error"));
    const form = new FormData();
    form.append("file", file);
    xhr.send(form);
  });
}

export const api = {
  selectMode: (jobId: string, mode: string) =>
    request<JobResponse>(`/format/select-mode`, {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, format_mode: mode }),
    }),

  analyze: (jobId: string) =>
    request<JobResponse>(`/format/analyze?job_id=${jobId}`, { method: "POST" }),

  execute: (jobId: string) =>
    request<JobResponse>(`/format/execute?job_id=${jobId}`, { method: "POST" }),

  customize: (jobId: string, settings: FormatSettings) =>
    request<{ status: string }>("/format/customize", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, settings }),
    }),

  getJob: (jobId: string) =>
    request<JobResponse>(`/format/job/${jobId}`),

  getPreview: (jobId: string) =>
    request<PreviewResponse>(`/preview/${jobId}`),

  getTemplates: () =>
    request<TemplateInfo[]>("/templates/"),

  saveTemplate: (name: string, settingsJson: string) =>
    request<TemplateInfo>("/templates/save", {
      method: "POST",
      body: JSON.stringify({ name, settings_json: settingsJson }),
    }),

  deleteTemplate: (id: number) =>
    request<{ status: string }>(`/templates/${id}`, { method: "DELETE" }),

  getDownloadUrl: (jobId: string, fmt: "docx" | "pdf" = "docx") =>
    `${BASE}/download/${jobId}?format=${fmt}`,

  extractImages: (jobId: string) =>
    request<ImageExtractResponse>(`/format-images/${jobId}/extract`),

  formatImages: (jobId: string, widthRatio: number = 0.7, imageRatios?: Record<number, number>, alignment?: string) =>
    request<{ job_id: string; image_count: number; message: string }>(
      `/format-images/${jobId}`,
      {
        method: "POST",
        body: JSON.stringify({ width_ratio: widthRatio, image_ratios: imageRatios, alignment }),
      },
    ),

  listSchoolTemplates: () =>
    request<{ templates: SchoolTemplateSummary[]; count: number }>("/school-templates/"),

  getSchoolTemplate: (templateId: string) =>
    request<SchoolTemplateDetail>(`/school-templates/${templateId}`),

  getSchoolTemplateSettings: (templateId: string) =>
    request<FormatSettings>(`/school-templates/${templateId}/settings`),

  saveSchoolTemplate: (name: string, description: string, formatSettings: FormatSettings) =>
    request<{ id: string; name: string; message: string }>("/school-templates/", {
      method: "POST",
      body: JSON.stringify({ name, description, format_settings: formatSettings }),
    }),
};

import type {
  JobResponse,
  PreviewResponse,
  TemplateInfo,
  FormatSettings,
  ImageExtractResponse,
  SchoolTemplateSummary,
  SchoolTemplateDetail,
} from "../types";
