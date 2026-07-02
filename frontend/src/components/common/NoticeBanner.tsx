import { useState } from "react";

const STORAGE_KEY = "paper-formatter-notice-collapsed";

function getInitialCollapsed(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

const NOTICE_ITEMS = [
  "表格和图片在排版时不会被修改，原样保留",
  "标题层级（一级/二级/三级）请在原稿中用 Word 样式标记清楚，否则可能识别错误",
  "图表编号请按「图1-1」「表2-3」格式标注，便于识别",
  "目录请用 Word「引用 → 目录」功能生成，本工具仅统一目录字体样式",
  "排版后请仔细检查，确认格式无误后再提交",
];

const NOTICE_ICONS = [
  <svg key="0" className="w-4 h-4 text-yellow-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>,
  <svg key="1" className="w-4 h-4 text-yellow-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h11" /></svg>,
  <svg key="2" className="w-4 h-4 text-yellow-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>,
  <svg key="3" className="w-4 h-4 text-yellow-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>,
  <svg key="4" className="w-4 h-4 text-yellow-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
];

export default function NoticeBanner() {
  const [collapsed, setCollapsed] = useState(getInitialCollapsed);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    try {
      localStorage.setItem(STORAGE_KEY, String(next));
    } catch {
      // localStorage unavailable
    }
  };

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-xl overflow-hidden animate-fade-in-up">
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-yellow-100/80 transition-colors duration-200"
      >
        <div className="flex items-center gap-2.5">
          <svg className="w-5 h-5 text-yellow-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
          </svg>
          <span className="text-sm font-semibold text-yellow-800">使用注意事项</span>
        </div>
        <svg
          className={`w-4 h-4 text-yellow-600 transition-transform duration-300 ${collapsed ? "" : "rotate-90"}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {!collapsed && (
        <ul className="px-4 pb-3.5 space-y-2 animate-slide-down">
          {NOTICE_ITEMS.map((item, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm text-yellow-700">
              {NOTICE_ICONS[i]}
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
