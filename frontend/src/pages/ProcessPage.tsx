import { useState, useEffect, useCallback, useRef } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";
import type { JobResponse, FlowState } from "../types";
import StepNavigation from "../components/common/StepNavigation";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorAlert from "../components/common/ErrorAlert";
import WarningBanner from "../components/common/WarningBanner";
import ModeSelector from "../modules/analyze/ModeSelector";
import StructureTree from "../modules/analyze/StructureTree";
import ResultPreview from "../modules/result/ResultPreview";
import TemplateManager from "../modules/template/TemplateManager";
import FormatSettingsPanel from "../modules/format/FormatSettingsPanel";
import ImageComparePanel from "../modules/image-compare/ImageComparePanel";
import SchoolTemplateSelector from "../modules/school-template/SchoolTemplateSelector";
import NoticeBanner from "../components/common/NoticeBanner";
import PrivacyBanner from "../components/common/PrivacyBanner";
import TextStatsBanner from "../components/common/TextStatsBanner";

export default function ProcessPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<JobResponse | null>(null);
  const [state, setState] = useState<FlowState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [previewKey, setPreviewKey] = useState(0);
  const [lastAppliedSettings, setLastAppliedSettings] = useState<Record<string, any> | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    if (!jobId) return;
    const controller = new AbortController();
    api.getJob(jobId, controller.signal).then((j) => {
      if (!mountedRef.current) return;
      setJob(j);
      setState(mapStatus(j.status));
    }).catch((e) => {
      if (e.name === "AbortError") return;
      if (!mountedRef.current) return;
      setError(e.message);
    });
    return () => {
      mountedRef.current = false;
      controller.abort();
    };
  }, [jobId]);

  const mapStatus = (status: string): FlowState => {
    switch (status) {
      case "UPLOADED": return "selecting";
      case "ANALYZING": return "analyzing";
      case "ANALYZED": return "analyzed";
      case "FORMATTING": return "formatting";
      case "COMPLETED": return "done";
      case "FAILED": return "error";
      default: return "idle";
    }
  };

  const handleSelectMode = useCallback(async (mode: string) => {
    if (!jobId) return;
    try {
      const updated = await api.selectMode(jobId, mode);
      if (!mountedRef.current) return;
      setJob(updated);
      setState("analyzing");

      const result = await api.analyze(jobId);
      if (!mountedRef.current) return;
      setJob(result);
      setState("analyzed");

      if (mode === "auto") {
        setState("formatting");
        const formatted = await api.execute(jobId);
        if (!mountedRef.current) return;
        setJob(formatted);
        setState("done");
      }
    } catch (e: any) {
      if (!mountedRef.current) return;
      setError(e.message);
      setState("error");
    }
  }, [jobId]);

  const handleApplySettings = useCallback(async (settings: Record<string, any>) => {
    if (!jobId) return;
    try {
      await api.customize(jobId, settings as any);
      if (!mountedRef.current) return;
      setState("formatting");
      setLastAppliedSettings(settings);
      const result = await api.execute(jobId);
      if (!mountedRef.current) return;
      setJob(result);
      setState("done");
      setPreviewKey(k => k + 1);
      setToast("应用完成");
      setTimeout(() => setToast(null), 2500);
    } catch (e: any) {
      if (!mountedRef.current) return;
      setError(e.message);
      setState("error");
    }
  }, [jobId]);

  const handleManualConfirm = useCallback(async () => {
    if (!jobId) return;
    try {
      setState("formatting");
      const result = await api.execute(jobId);
      if (!mountedRef.current) return;
      setJob(result);
      setState("done");
    } catch (e: any) {
      if (!mountedRef.current) return;
      setError(e.message);
      setState("error");
    }
  }, [jobId]);

  if (!jobId) return <ErrorAlert message="缺少任务ID" />;

  const nonLoadingStates: FlowState[] = ["idle", "selecting", "analyzed", "done"];
  const currentIdx = nonLoadingStates.indexOf(state);

  const goBack = () => {
    if (currentIdx > 0) {
      setState(nonLoadingStates[currentIdx - 1]);
      setError(null);
    }
  };

  const goForward = async () => {
    if (currentIdx < nonLoadingStates.length - 1) {
      const next = nonLoadingStates[currentIdx + 1];
      if (state === "selecting") {
        handleSelectMode("auto");
        return;
      }
      if (state === "analyzed") {
        handleManualConfirm();
        return;
      }
      setState(next);
      setError(null);
    }
  };

  const canGoBack = currentIdx > 0 && state !== "analyzing" && state !== "formatting";
  const canGoForward = currentIdx < nonLoadingStates.length - 1 && state !== "analyzing" && state !== "formatting" && state !== "error";

  return (
    <div className="max-w-2xl mx-auto space-y-4 relative">
      <NoticeBanner />

      <StepNavigation state={state} />

      {error && <ErrorAlert message={error} onRetry={() => setError(null)} />}

      {/* ── 应用完成 Toast ── */}
      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-green-600 text-white px-5 py-2.5 rounded-xl shadow-lg flex items-center gap-2 animate-fade-in-up text-sm font-medium">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {toast}
        </div>
      )}

      {state === "idle" && <LoadingSpinner message="获取任务信息..." />}

      {state === "selecting" && (
        <ModeSelector onSelect={handleSelectMode} loading={false} />
      )}

      {(state === "analyzing" || state === "formatting") && (
        <LoadingSpinner
          message={state === "analyzing" ? "AI 正在分析论文结构..." : "正在排版中..."}
        />
      )}

      {state === "analyzed" && job?.analysis && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-1">
              {job.analysis.title}
            </h3>
            <StructureTree sections={job.analysis.sections} />
          </div>
          {job.char_count > 0 && (
            <TextStatsBanner charCount={job.char_count} estimatedPages={job.estimated_pages} />
          )}
          {job.warnings && <WarningBanner warnings={job.warnings} />}
          <div className="flex justify-end">
            <button
              onClick={handleManualConfirm}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
            >
              确认，开始排版
            </button>
          </div>
        </div>
      )}

      {state === "done" && jobId && (
        <div className="space-y-6">
          {/* ── 下载按钮（始终可见）── */}
          <div className="bg-white rounded-xl border p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载排版结果
            </h3>
            <div className="flex items-center gap-3 flex-wrap">
              <a
                href={api.getDownloadUrl(jobId, "docx")}
                className="group inline-flex items-center gap-2.5 px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 active:scale-95 transition-all duration-200 shadow-sm hover:shadow-md"
              >
                <svg className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                下载 Word
              </a>
              <a
                href={api.getDownloadUrl(jobId, "pdf")}
                className="group inline-flex items-center gap-2.5 px-5 py-2.5 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 active:scale-95 transition-all duration-200 shadow-sm hover:shadow-md"
              >
                <svg className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                下载 PDF
              </a>
            </div>
            <p className="text-xs text-gray-400 flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
              </svg>
              调整下方图片尺寸或格式设置后，重新排版再下载即可更新
            </p>
          </div>

          <ResultPreview key={previewKey} jobId={jobId} />
          <ImageComparePanel jobId={jobId} onImagesUpdated={() => setPreviewKey(k => k + 1)} />
          <SchoolTemplateSelector jobId={jobId} onApply={handleApplySettings} currentSettings={lastAppliedSettings as any} onSettingsRefreshed={() => setPreviewKey(k => k + 1)} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TemplateManager />
            <FormatSettingsPanel onApply={handleApplySettings} />
          </div>
        </div>
      )}

      <PrivacyBanner />

      {canGoBack && (
        <button
          onClick={goBack}
          className="fixed left-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white border border-gray-300 shadow-md flex items-center justify-center hover:bg-gray-50 hover:border-indigo-300 transition-colors z-40"
          title="后退一步"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}
      {canGoForward && (
        <button
          onClick={goForward}
          className="fixed right-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-indigo-600 border border-indigo-600 shadow-md flex items-center justify-center hover:bg-indigo-700 transition-colors z-40"
          title="前进一步"
        >
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      )}
    </div>
  );
}
