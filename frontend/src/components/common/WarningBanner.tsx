import type { FormatWarnings } from "../../types";

interface Props {
  warnings: FormatWarnings;
}

const LABELS: Record<string, string> = {
  missing_abstract: "缺少摘要",
  missing_toc: "缺少目录",
  missing_references: "缺少参考文献",
  missing_figure_labels: "图中缺少图序标注",
  missing_table_labels: "表中缺少表序标注",
  conflicting_headings: "标题编号可能跳跃",
};

export default function WarningBanner({ warnings }: Props) {
  const items = Object.entries(warnings)
    .filter(([, v]) => v)
    .map(([k]) => LABELS[k] || k);

  if (items.length === 0) return null;

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-3.5 animate-fade-in">
      <div className="flex items-center gap-2 mb-2">
        <svg className="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <p className="text-amber-800 text-sm font-semibold">格式提醒</p>
      </div>
      <ul className="space-y-1">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-2 text-amber-700 text-xs">
            <span className="w-1 h-1 rounded-full bg-amber-400 shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
