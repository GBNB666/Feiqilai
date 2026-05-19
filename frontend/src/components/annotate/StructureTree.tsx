import type { PaperStructure, Section } from "@/types"
import { ChevronRight } from "lucide-react"

interface Props {
  structure: PaperStructure
  onSelectSection: (section: Section) => void
  selectedSection: Section | null
}

export function StructureTree({ structure, onSelectSection, selectedSection }: Props) {
  return (
    <div className="border rounded-lg p-4">
      <h3 className="font-semibold mb-3 text-sm">论文结构</h3>
      <div className="space-y-1">
        {structure.title && (
          <div className="text-sm font-medium text-primary mb-2 px-2">{structure.title}</div>
        )}
        {structure.sections.map((section, i) => (
          <button
            key={i}
            onClick={() => onSelectSection(section)}
            className={`w-full text-left px-2 py-1.5 rounded text-sm flex items-center gap-2 transition-colors ${
              selectedSection?.start_marker === section.start_marker
                ? "bg-primary/10 text-primary font-medium"
                : "hover:bg-muted"
            }`}
            style={{ paddingLeft: `${8 + section.level * 16}px` }}
          >
            <ChevronRight className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">{section.title}</span>
            {section.has_figures && (
              <span className="text-xs bg-amber-100 text-amber-700 px-1 rounded shrink-0">图</span>
            )}
            {section.has_tables && (
              <span className="text-xs bg-blue-100 text-blue-700 px-1 rounded shrink-0">表</span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}
