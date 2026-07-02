import type { SectionInfo } from "../../types";

interface Props {
  sections: SectionInfo[];
}

const LEVEL_STYLES: Record<number, string> = {
  1: "text-indigo-700 font-semibold",
  2: "text-blue-700 font-medium",
  3: "text-gray-700",
  4: "text-gray-500",
};

const LEVEL_DOTS: Record<number, string> = {
  1: "bg-indigo-500",
  2: "bg-blue-500",
  3: "bg-gray-400",
  4: "bg-gray-300",
};

const LEVEL_INDENTS: Record<number, string> = {
  1: "ml-0",
  2: "ml-5",
  3: "ml-10",
  4: "ml-14",
};

export default function StructureTree({ sections }: Props) {
  return (
    <div className="space-y-0.5">
      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
        识别结构
      </h3>
      {sections.map((sec, i) => (
        <div
          key={i}
          className={`${LEVEL_INDENTS[sec.level] || "ml-0"} flex items-center gap-2.5 py-1 group hover:bg-gray-50 rounded-md px-1 -mx-1 transition-colors duration-150`}
        >
          {/* Level dot */}
          <span className={`w-2 h-2 rounded-full shrink-0 ${LEVEL_DOTS[sec.level] || "bg-gray-300"}`} />
          <span className={`text-sm ${LEVEL_STYLES[sec.level] || "text-gray-600"}`}>
            {sec.numbering}
            {sec.title}
          </span>
          {sec.has_figures && (
            <span className="flex items-center gap-0.5 text-[10px] text-purple-500 bg-purple-50 px-1.5 py-0.5 rounded font-medium">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              图
            </span>
          )}
          {sec.has_tables && (
            <span className="flex items-center gap-0.5 text-[10px] text-green-600 bg-green-50 px-1.5 py-0.5 rounded font-medium">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              表
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
