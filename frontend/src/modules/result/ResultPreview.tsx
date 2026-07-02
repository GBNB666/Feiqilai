import { useEffect, useState } from "react";
import { api } from "../../services/api";
import type { PreviewResponse } from "../../types";

interface Props {
  jobId: string;
}

const TOC_HINT = "如需设置目录格式，请在下方「格式设置」中调整「目录标题」和「目录条目」的字体、字号等参数。";

/** Chinese字号 → pt mapping */
const PT_LABELS: Record<number, string> = {
  42: "初号", 36: "小初", 26: "一号", 24: "小一", 22: "二号",
  18: "小二", 16: "三号", 15: "小三", 14: "四号", 12: "小四",
  10.5: "五号", 9: "小五",
};

function ptLabel(pt: number | null | undefined): string {
  if (pt == null) return "";
  return PT_LABELS[pt] || `${pt}pt`;
}

const ALIGN_LABELS: Record<string, string> = {
  LEFT: "左对齐", CENTER: "居中", RIGHT: "右对齐",
  JUSTIFY: "两端对齐", DISTRIBUTE: "分散对齐",
};

export default function ResultPreview({ jobId }: Props) {
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getPreview(jobId)
      .then((data) => { if (!cancelled) { setPreview(data); setError(null); } })
      .catch((e) => { if (!cancelled) setError(e.message || "预览加载失败"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center gap-3 py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-3 border-indigo-200 border-t-indigo-600" />
        <p className="text-sm text-gray-400">加载预览中…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
        <svg className="w-5 h-5 text-red-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p className="text-sm font-medium text-red-700">预览加载失败</p>
          <p className="text-xs text-red-500 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 animate-fade-in-up">
      <div className="flex items-center gap-2">
        <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <h3 className="text-sm font-semibold text-gray-700">排版结果预览</h3>
        {preview && (
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
            {preview.sections.length} 段
          </span>
        )}
      </div>

      {/* TOC hint */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg px-3.5 py-2.5 flex items-start gap-2">
        <svg className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
        </svg>
        <p className="text-xs text-blue-700">{TOC_HINT}</p>
      </div>

      {(!preview || preview.sections.length === 0) ? (
        <div className="flex flex-col items-center gap-2 py-10 text-gray-400 border rounded-xl bg-white">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">暂无预览数据</p>
        </div>
      ) : (
        <div className="border rounded-xl divide-y max-h-[600px] overflow-y-auto bg-white shadow-sm">
          {preview.sections.map((sec, i) => (
            <div key={i} className="p-3.5 hover:bg-gray-50/70 transition-colors duration-150">
              {/* Title + level badge */}
              <div className="flex items-center gap-2 mb-1.5">
                <span className="shrink-0 text-[10px] font-medium text-indigo-500 bg-indigo-50 px-1.5 py-0.5 rounded">
                  L{sec.level || "?"}
                </span>
                <h4 className="text-sm font-medium text-gray-800 truncate">
                  {sec.title || "(无标题)"}
                </h4>
              </div>

              {/* Font format badges */}
              {sec.font_info && (sec.font_info.font_name || sec.font_info.font_size_pt) && (
                <div className="flex flex-wrap items-center gap-1 mb-2 ml-7">
                  {sec.font_info.font_name && (
                    <span className="text-[10px] font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                      {sec.font_info.font_name}
                    </span>
                  )}
                  {sec.font_info.font_size_pt && (
                    <span className="text-[10px] font-medium text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
                      {ptLabel(sec.font_info.font_size_pt)} ({sec.font_info.font_size_pt}pt)
                    </span>
                  )}
                  {sec.font_info.bold && (
                    <span className="text-[10px] font-medium text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                      加粗
                    </span>
                  )}
                  {sec.font_info.alignment && ALIGN_LABELS[sec.font_info.alignment] && (
                    <span className="text-[10px] font-medium text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded">
                      {ALIGN_LABELS[sec.font_info.alignment]}
                    </span>
                  )}
                </div>
              )}

              {/* Body sample */}
              {sec.body_sample && (
                <div className="ml-7 mb-2 bg-gray-50 rounded-lg p-2.5 border border-gray-100">
                  <span className="text-[10px] text-gray-400 block mb-1">正文示例</span>
                  <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">
                    {sec.body_sample.text}
                  </p>
                  {sec.body_sample.font_info && (
                    <div className="flex flex-wrap items-center gap-1 mt-1.5">
                      {sec.body_sample.font_info.font_name && (
                        <span className="text-[10px] text-emerald-600">{sec.body_sample.font_info.font_name}</span>
                      )}
                      {sec.body_sample.font_info.font_size_pt && (
                        <span className="text-[10px] text-blue-600">
                          {ptLabel(sec.body_sample.font_info.font_size_pt)} ({sec.body_sample.font_info.font_size_pt}pt)
                        </span>
                      )}
                      {sec.body_sample.font_info.alignment && ALIGN_LABELS[sec.body_sample.font_info.alignment] && (
                        <span className="text-[10px] text-purple-600">{ALIGN_LABELS[sec.body_sample.font_info.alignment]}</span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Content — 只取一小段 */}
              {sec.content.slice(0, 1).map((c, j) => (
                <p key={j} className="text-xs text-gray-500 truncate ml-7">{c.slice(0, 80)}{c.length > 80 ? "…" : ""}</p>
              ))}

              {/* Image/table markers */}
              {sec.markers.length > 0 && (
                <div className="flex gap-1.5 mt-2 ml-7">
                  {sec.markers.map((m, j) => (
                    <span key={j} className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded font-medium">
                      {m.label}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
