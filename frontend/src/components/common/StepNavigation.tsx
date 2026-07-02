import { cn } from "../../lib/utils";
import type { FlowState } from "../../types";
import type { ReactNode } from "react";

const STEPS: { key: FlowState; label: string; icon: ReactNode }[] = [
  { key: "selecting", label: "上传", icon: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  )},
  { key: "analyzing", label: "AI分析", icon: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  )},
  { key: "analyzed", label: "确认", icon: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )},
  { key: "formatting", label: "排版", icon: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M4 6h16M4 12h16m-7 6h7" />
    </svg>
  )},
  { key: "done", label: "完成", icon: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  )},
];

interface Props {
  state: FlowState;
}

export default function StepNavigation({ state }: Props) {
  const currentIdx = state === "error" ? -1 : STEPS.findIndex((s) => s.key === state);

  return (
    <div className="flex items-center justify-center gap-1 mb-6 animate-fade-in-up">
      {STEPS.map((step, i) => (
        <div key={step.key} className="flex items-center gap-1">
          <div className="flex flex-col items-center gap-1">
            <div
              className={cn(
                "flex items-center justify-center w-9 h-9 rounded-full text-xs font-medium transition-all duration-300",
                i < currentIdx
                  ? "bg-indigo-600 text-white shadow-sm"
                  : i === currentIdx
                    ? "bg-indigo-100 text-indigo-700 border-2 border-indigo-400 shadow-sm ring-2 ring-indigo-100"
                    : "bg-gray-100 text-gray-400"
              )}
            >
              {i < currentIdx ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                step.icon
              )}
            </div>
            <span
              className={cn(
                "text-[10px] transition-colors duration-300",
                i <= currentIdx ? "text-indigo-700 font-medium" : "text-gray-400"
              )}
            >
              {step.label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={cn(
              "w-8 h-0.5 rounded-full transition-colors duration-300 mb-4",
              i < currentIdx ? "bg-indigo-400" : "bg-gray-200"
            )} />
          )}
        </div>
      ))}
    </div>
  );
}
