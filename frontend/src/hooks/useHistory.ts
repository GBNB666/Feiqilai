import { useState, useCallback } from "react"
import type { HistoryRecord } from "@/types"

const KEY = "paper_formatter_history"
const MAX = 10
const TTL_MS = 24 * 60 * 60 * 1000 // 24h

function load(): HistoryRecord[] {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const now = Date.now()
    const records: HistoryRecord[] = JSON.parse(raw)
    return records.filter((r) => now - r.timestamp < TTL_MS)
  } catch {
    return []
  }
}

function save(records: HistoryRecord[]) {
  localStorage.setItem(KEY, JSON.stringify(records.slice(0, MAX)))
}

export function formatRelativeTime(ts: number): string {
  const diff = Math.max(0, Date.now() - ts)
  const sec = Math.floor(diff / 1000)
  if (sec < 60) return "刚刚"
  const min = Math.floor(sec / 60)
  if (min < 60) return `${min}分钟前`
  const hour = Math.floor(min / 60)
  if (hour < 24) return `${hour}小时前`
  return ""
}

export function useHistory() {
  const [records, setRecords] = useState<HistoryRecord[]>(load)

  const addRecord = useCallback((r: HistoryRecord) => {
    const now = Date.now()
    const existing = load()
    // Deduplicate: replace if same jobId
    const filtered = existing.filter((x) => x.jobId !== r.jobId && now - x.timestamp < TTL_MS)
    const next = [{ ...r, timestamp: now }, ...filtered].slice(0, MAX)
    save(next)
    setRecords(next)
  }, [])

  const clearHistory = useCallback(() => {
    localStorage.removeItem(KEY)
    setRecords([])
  }, [])

  return { records, addRecord, clearHistory }
}
