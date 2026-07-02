export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    UPLOADED: "已上传",
    ANALYZING: "AI分析中",
    ANALYZED: "分析完成",
    FORMATTING: "排版中",
    COMPLETED: "排版完成",
    FAILED: "失败",
  };
  return map[status] || status;
}
