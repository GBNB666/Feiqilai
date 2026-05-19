import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Save, FolderOpen, Trash2, X } from "lucide-react"
import type { TemplateInfo, FormatSettings } from "@/types"

interface Props {
  templates: TemplateInfo[]
  currentSettings: FormatSettings
  onSave: (name: string) => Promise<void>
  onLoad: (settings: FormatSettings) => void
  onDelete: (id: number) => Promise<void>
}

export function TemplateManager({ templates, currentSettings, onSave, onLoad, onDelete }: Props) {
  const [name, setName] = useState("")
  const [showSave, setShowSave] = useState(false)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!name.trim()) return
    setSaving(true)
    try {
      await onSave(name.trim())
      setName("")
      setShowSave(false)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => setShowSave(!showSave)}>
          <Save className="w-3.5 h-3.5 mr-1" />
          保存模板
        </Button>
        {showSave && (
          <div className="flex items-center gap-1">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="模板名称"
              className="h-8 w-32 text-xs"
              onKeyDown={(e) => e.key === "Enter" && handleSave()}
            />
            <Button size="sm" onClick={handleSave} disabled={saving || !name.trim()} className="h-8 text-xs">保存</Button>
            <button onClick={() => setShowSave(false)}><X className="w-3.5 h-3.5" /></button>
          </div>
        )}
      </div>

      {templates.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          <FolderOpen className="w-3.5 h-3.5 text-muted-foreground shrink-0 mt-0.5" />
          {templates.map((t) => (
            <button
              key={t.id}
              onClick={() => onLoad(t.settings)}
              className="group flex items-center gap-1 bg-muted/50 hover:bg-muted rounded px-2 py-1 text-xs transition-colors"
            >
              <span>{t.name}</span>
              <span
                className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600"
                onClick={(e) => { e.stopPropagation(); onDelete(t.id) }}
              >
                <Trash2 className="w-3 h-3" />
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
