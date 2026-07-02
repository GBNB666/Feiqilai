import { useEffect, useState, useRef, useCallback } from "react";
import { api } from "../../services/api";
import type { ExtractedImage } from "../../types";

interface Props {
  jobId: string;
  onImagesUpdated?: () => void;
}

export default function ImageComparePanel({ jobId, onImagesUpdated }: Props) {
  const [images, setImages] = useState<ExtractedImage[]>([]);
  const [pageWidthEmu, setPageWidthEmu] = useState(0);
  const [ratios, setRatios] = useState<Record<number, number>>({});
  const [alignments, setAlignments] = useState<Record<number, string>>({});
  const [globalAlignment, setGlobalAlignment] = useState<string>("CENTER");
  const globalAlignmentRef = useRef(globalAlignment);
  globalAlignmentRef.current = globalAlignment;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [applyingIdx, setApplyingIdx] = useState<number | null>(null);
  const [successIdx, setSuccessIdx] = useState<number | null>(null);
  const debounceRef = useRef<Record<number, ReturnType<typeof setTimeout>>>({});

  useEffect(() => {
    api.extractImages(jobId)
      .then((data) => {
        setImages(data.images);
        setPageWidthEmu(data.page_width_usable_emu);
        // 初始化所有图片比例为 70%，对齐方式为居中
        const init: Record<number, number> = {};
        const initAlign: Record<number, string> = {};
        data.images.forEach((_, i) => { init[i] = 0.7; initAlign[i] = "CENTER"; });
        setRatios(init);
        setAlignments(initAlign);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [jobId]);

  // 将当前所有比例+对齐写入后端
  const applyAll = useCallback(async (newRatios: Record<number, number>, changedIdx: number, align?: string) => {
    setApplyingIdx(changedIdx);
    try {
      const res = await api.formatImages(jobId, 0.7, newRatios, align || globalAlignmentRef.current);
      setSuccessIdx(changedIdx);
      setTimeout(() => setSuccessIdx(null), 2000);
      onImagesUpdated?.();
      return res;
    } catch (e: any) {
      setError(e.message);
    } finally {
      setApplyingIdx(null);
    }
  }, [jobId]);

  // 修改单张图片比例（带防抖自动应用）
  const handleRatioChange = (idx: number, newRatio: number) => {
    const updated = { ...ratios, [idx]: newRatio };
    setRatios(updated);

    // 防抖 400ms 后自动应用
    if (debounceRef.current[idx]) {
      clearTimeout(debounceRef.current[idx]);
    }
    debounceRef.current[idx] = setTimeout(() => {
      applyAll(updated, idx);
    }, 400);
  };

  // 即时应用（onMouseUp / onTouchEnd）
  const handleApplyNow = (idx: number) => {
    if (debounceRef.current[idx]) {
      clearTimeout(debounceRef.current[idx]);
    }
    applyAll(ratios, idx);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-3 py-8 text-gray-400 text-sm">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-500" />
        正在提取文档图片...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-600 flex items-center justify-between">
        {error}
        <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600 ml-2">✕</button>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="bg-white rounded-xl border p-6 text-center text-gray-400 text-sm">
        <svg className="w-8 h-8 mx-auto mb-2 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        此文档中没有图片
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in-up">
      {/* Header */}
      <div className="flex items-center gap-2">
        <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 className="text-sm font-semibold text-gray-700">
          图片尺寸调整
        </h3>
        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
          {images.length} 张
        </span>
      </div>

      {/* Hint + Global alignment */}
      <div className="flex items-center justify-between -mt-3">
        <p className="text-xs text-gray-400">
          拖动滑块调整每张图片的宽度比例，松手后自动应用
        </p>
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-gray-400">全局对齐</span>
          <select
            value={globalAlignment}
            onChange={(e) => setGlobalAlignment(e.target.value)}
            className="text-xs border rounded px-1.5 py-0.5 bg-white"
          >
            <option value="LEFT">左对齐</option>
            <option value="CENTER">居中</option>
            <option value="RIGHT">右对齐</option>
          </select>
        </div>
      </div>

      {/* Image Cards */}
      <div className="space-y-4">
        {images.map((img, idx) => {
          const ratio = ratios[idx] ?? 0.7;
          const ratioPct = Math.round(ratio * 100);
          const desiredEmu = pageWidthEmu * ratio;
          const scale = img.width_emu > 0 ? desiredEmu / img.width_emu : ratio;
          const clampedScale = Math.max(0.1, Math.min(3.0, scale));
          const isApplying = applyingIdx === idx;
          const isSuccess = successIdx === idx;

          return (
            <div key={img.index} className="bg-white rounded-xl border overflow-hidden">
              {/* Card header */}
              <div className="px-4 py-2 bg-gray-50/70 border-b flex items-center gap-2 flex-wrap">
                <span className="text-xs font-medium text-gray-600">
                  图片 {img.index + 1}
                </span>
                <span className="text-[10px] text-gray-400">
                  {img.content_type.split("/")[1]?.toUpperCase()}
                </span>
                <span className="text-[10px] text-gray-400">
                  原始: {(img.width_emu / 9525).toFixed(0)}px
                </span>
                <span className="text-[10px] text-gray-400">
                  预览: {(img.width_emu / 9525 * clampedScale).toFixed(0)}px
                </span>
                {/* Per-image alignment */}
                <select
                  value={alignments[idx] || "CENTER"}
                  onChange={(e) => {
                    const v = e.target.value;
                    const updated = { ...alignments, [idx]: v };
                    setAlignments(updated);
                    applyAll(ratios, idx, v);
                  }}
                  className="ml-auto text-[10px] border rounded px-1 py-0.5 bg-white text-gray-500"
                >
                  <option value="LEFT">左对齐</option>
                  <option value="CENTER">居中</option>
                  <option value="RIGHT">右对齐</option>
                </select>
                {/* Status indicator */}
                {isApplying && (
                  <span className="ml-auto text-[10px] text-indigo-500 flex items-center gap-1">
                    <span className="h-2.5 w-2.5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-500" />
                    应用中...
                  </span>
                )}
                {isSuccess && (
                  <span className="ml-auto text-[10px] text-green-500 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    已应用
                  </span>
                )}
              </div>

              {/* Ghost + Scaled container — alignment reflects chosen setting */}
              {(() => {
                const al = alignments[idx] || "CENTER";
                const justify = al === "LEFT" ? "justify-start" : al === "RIGHT" ? "justify-end" : "justify-center";
                return (
              <div className={`p-4 flex ${justify} bg-[#fafafa]`}>
                <div
                  className="relative inline-block"
                  style={{ width: img.width_emu / 9525 + "px" }}
                >
                  {/* Ghost — static original */}
                  <img
                    src={img.base64}
                    alt={`Original ${img.index + 1}`}
                    className="block w-full opacity-[0.22] grayscale outline-2 outline-dashed outline-gray-400/55 outline-offset-2 rounded-sm"
                    style={{ transition: "none" as any }}
                  />

                  {/* Scaled preview — overlaid, CSS scaled */}
                  <img
                    src={img.base64}
                    alt={`Preview ${img.index + 1}`}
                    className="absolute top-0 left-0 origin-top-left shadow-md rounded-sm"
                    style={{
                      transform: `scale(${clampedScale})`,
                      transition: "none" as any,
                    }}
                  />
                </div>
              </div>
                );
              })()}

              {/* Per-image slider */}
              <div className="px-4 py-3 bg-gray-50/50 border-t space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">宽度比例</span>
                  <span className="text-sm font-bold text-indigo-600 tabular-nums">
                    {ratioPct}%
                  </span>
                </div>
                <input
                  type="range"
                  min={30}
                  max={100}
                  step={5}
                  value={ratioPct}
                  onChange={(e) => handleRatioChange(idx, Number(e.target.value) / 100)}
                  onMouseUp={() => handleApplyNow(idx)}
                  onTouchEnd={() => handleApplyNow(idx)}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
                <div className="flex justify-between px-1">
                  {[30, 50, 70, 85, 100].map((t) => (
                    <span
                      key={t}
                      className="text-[10px] text-gray-400 cursor-pointer hover:text-indigo-500 transition-colors"
                      onClick={() => {
                        handleRatioChange(idx, t / 100);
                        // 点击刻度立即应用
                        const updated = { ...ratios, [idx]: t / 100 };
                        setRatios(updated);
                        if (debounceRef.current[idx]) clearTimeout(debounceRef.current[idx]);
                        applyAll(updated, idx);
                      }}
                    >
                      {t}%
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
