import { Outlet, useNavigate, useLocation } from "react-router-dom";

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const isHome = location.pathname === "/";

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-30 shadow-sm">
        <div className="mx-auto max-w-5xl px-4 py-3 flex items-center gap-3">
          {/* Logo icon */}
          <div
            className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center cursor-pointer hover:bg-indigo-700 transition-colors"
            onClick={() => navigate("/")}
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div
            className="flex items-baseline gap-2 cursor-pointer"
            onClick={() => navigate("/")}
          >
            <span className="text-lg font-bold text-gray-800">论文排版</span>
            <span className="text-xs text-gray-400 font-medium">Paper Formatter</span>
          </div>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Restart button — only show when not on home page */}
          {!isHome && (
            <button
              onClick={() => navigate("/")}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-500 bg-gray-100 rounded-lg hover:bg-indigo-50 hover:text-indigo-600 active:scale-95 transition-all duration-200"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              重新开始
            </button>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
