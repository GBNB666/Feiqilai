interface Props {
  charCount: number;
  estimatedPages: number;
}

export default function TextStatsBanner({ charCount, estimatedPages }: Props) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-sm animate-fade-in">
      <div className="flex items-center gap-5 text-sm">
        {/* Char count */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center">
            <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <span className="font-semibold text-gray-800">{charCount.toLocaleString()}</span>
            <span className="text-gray-400 ml-1">字</span>
          </div>
        </div>

        <span className="text-gray-200 font-light">|</span>

        {/* Page estimate */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <span className="font-semibold text-gray-800">{estimatedPages}</span>
            <span className="text-gray-400 ml-1">页（预估）</span>
          </div>
        </div>
      </div>
    </div>
  );
}
