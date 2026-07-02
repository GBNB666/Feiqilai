import { useState, useCallback } from "react";
import type { SectionInfo } from "../../types";

interface EditableSection {
  level: number;
  numbering: string;
  title: string;
}

interface Props {
  sections: SectionInfo[];
  onConfirm: (edits: EditableSection[]) => void;
}

export default function AnnotationPanel({ sections, onConfirm }: Props) {
  const [edits, setEdits] = useState<EditableSection[]>(
    sections.map((sec) => ({
      level: sec.level ?? 1,
      numbering: sec.numbering ?? "",
      title: sec.title ?? "",
    }))
  );

  const updateField = useCallback(
    (index: number, field: keyof EditableSection, value: string | number) => {
      setEdits((prev) =>
        prev.map((e, i) => (i === index ? { ...e, [field]: value } : e))
      );
    },
    []
  );

  const handleConfirm = () => {
    onConfirm(edits);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">手动确认章节标注</h3>
        <button
          onClick={handleConfirm}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
        >
          确认，开始排版
        </button>
      </div>
      <div className="border rounded-lg divide-y">
        {edits.map((sec, i) => (
          <div key={i} className="flex items-center gap-3 p-3">
            <select
              value={sec.level}
              onChange={(e) => updateField(i, "level", Number(e.target.value))}
              className="text-sm border rounded px-2 py-1 bg-white"
            >
              <option value={0}>特殊</option>
              <option value={1}>一级标题</option>
              <option value={2}>二级标题</option>
              <option value={3}>三级标题</option>
              <option value={4}>四级标题</option>
            </select>
            <input
              value={sec.numbering}
              onChange={(e) => updateField(i, "numbering", e.target.value)}
              placeholder="编号"
              className="text-sm border rounded px-2 py-1 w-20"
            />
            <input
              value={sec.title}
              onChange={(e) => updateField(i, "title", e.target.value)}
              placeholder="标题"
              className="text-sm border rounded px-2 py-1 flex-1"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
