interface Props {
  onSelect: (mode: string) => void;
  loading: boolean;
}

export default function ModeSelector({ onSelect, loading }: Props) {
  return (
    <div className="flex flex-col items-center gap-6 py-12 animate-fade-in-up">
      <h2 className="text-xl font-semibold text-gray-800">选择排版模式</h2>
      <div className="flex gap-4 animate-stagger">
        {/* Auto mode */}
        <button
          onClick={() => onSelect("auto")}
          disabled={loading}
          className="group px-8 py-5 rounded-2xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] hover:shadow-lg shadow-md"
        >
          <div className="flex items-center justify-center gap-2 mb-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>自动排版</span>
          </div>
          <span className="block text-xs text-indigo-200">AI 识别结构，一键排版</span>
        </button>

        {/* Manual mode */}
        <button
          onClick={() => onSelect("manual")}
          disabled={loading}
          className="group px-8 py-5 rounded-2xl border border-gray-200 bg-white text-gray-700 font-medium hover:bg-gray-50 hover:border-gray-300 disabled:opacity-50 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] hover:shadow-md shadow-sm"
        >
          <div className="flex items-center justify-center gap-2 mb-2">
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            <span>手动标注</span>
          </div>
          <span className="block text-xs text-gray-400">自行标记章节结构</span>
        </button>
      </div>
    </div>
  );
}
