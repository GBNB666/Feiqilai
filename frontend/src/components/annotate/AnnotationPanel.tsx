import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { StructureTree } from "./StructureTree"
import type { PaperStructure, Section } from "@/types"

interface Props {
  structure: PaperStructure
  onSubmit: (annotations: string) => void
  disabled?: boolean
}

export function AnnotationPanel({ structure, onSubmit, disabled }: Props) {
  const [sections, setSections] = useState<Section[]>(() => [...(structure.sections || [])])
  const [selectedSection, setSelectedSection] = useState<Section | null>(null)
  const [editTitle, setEditTitle] = useState("")
  const [editLevel, setEditLevel] = useState("1")

  const handleSelectSection = (section: Section) => {
    setSelectedSection(section)
    setEditTitle(section.title)
    setEditLevel(String(section.level))
  }

  const handleUpdateSection = () => {
    if (!selectedSection) return
    const updated = sections.map((s) =>
      s.start_marker === selectedSection.start_marker
        ? { ...s, title: editTitle, level: parseInt(editLevel) }
        : s
    )
    setSections(updated)
    setSelectedSection(null)
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">校对论文结构</h2>
      <p className="text-sm text-muted-foreground">
        AI已识别出以下结构，点击章节进行校对修改，确认无误后提交排版。
      </p>
      <div className="grid sm:grid-cols-2 gap-6">
        <StructureTree
          structure={{ ...structure, sections }}
          onSelectSection={handleSelectSection}
          selectedSection={selectedSection}
        />
        {selectedSection && (
          <div className="border rounded-lg p-4 space-y-4">
            <h4 className="font-semibold">编辑章节</h4>
            <div className="space-y-2">
              <Label htmlFor="sec-title">标题</Label>
              <Input id="sec-title" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>层级</Label>
              <Select value={editLevel} onValueChange={setEditLevel}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">一级标题</SelectItem>
                  <SelectItem value="2">二级标题</SelectItem>
                  <SelectItem value="3">三级标题</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleUpdateSection} className="w-full" variant="outline" size="sm">
              确认修改
            </Button>
          </div>
        )}
      </div>
      <Button onClick={() => onSubmit(JSON.stringify({ ...structure, sections }))} disabled={disabled} className="w-full">
        确认结构，开始排版
      </Button>
    </div>
  )
}
