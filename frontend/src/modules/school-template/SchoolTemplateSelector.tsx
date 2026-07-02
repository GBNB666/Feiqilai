import { useEffect, useState } from "react";
import { api } from "../../services/api";
import type { SchoolTemplateSummary, SchoolTemplateDetail, FormatSettings } from "../../types";

interface Props {
  jobId?: string;
  onApply: (settings: FormatSettings) => void;
  currentSettings?: FormatSettings | null;
  onSettingsRefreshed?: () => void;
}

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

/** Strip parenthesized text (both Chinese and English parentheses) from descriptions. */
function cleanDescription(desc: string): string {
  return desc.replace(/[（(][^）)]*[）)]/g, "").replace(/\s+/g, " ").trim();
}

const CATEGORY_NAMES: Record<string, string> = {
  title: "论文标题",
  heading_1: "一级标题",
  heading_2: "二级标题",
  heading_3: "三级标题",
  body: "正文",
  table_caption: "表注",
  figure_caption: "图注",
  reference: "参考文献",
  toc_title: "目录标题",
  toc_entry: "目录条目",
  header_footer: "页眉页脚",
  table_text: "表格文字",
  page: "页面设置",
};

export default function SchoolTemplateSelector({ onApply, currentSettings, onSettingsRefreshed }: Props) {
  const [templates, setTemplates] = useState<SchoolTemplateSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<SchoolTemplateDetail | null>(null);
  const [expandedCat, setExpandedCat] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    api.listSchoolTemplates()
      .then((data) => setTemplates(data.templates))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = async (tid: string) => {
    if (selectedId === tid) {
      setSelectedId(null);
      setDetail(null);
      setExpandedCat(null);
      return;
    }
    setSelectedId(tid);
    setDetailLoading(true);
    setExpandedCat(null);
    try {
      const d = await api.getSchoolTemplate(tid);
      setDetail(d);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleApply = async () => {
    if (!selectedId) return;
    setApplying(true);
    setSuccessMsg(null);
    setError(null);
    try {
      const settings = await api.getSchoolTemplateSettings(selectedId);
      onApply(settings);
      setSuccessMsg(`已应用「${detail?.name || selectedId}」模板，正在重新排版...`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setApplying(false);
    }
  };

  const handleSaveCurrent = async () => {
    if (!currentSettings) return;
    const name = prompt("请输入模板名称（如：XX大学论文格式）：");
    if (!name?.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const res = await api.saveSchoolTemplate(name.trim(), "", currentSettings);
      setSuccessMsg(`已保存「${res.name}」`);
      // 重新加载模板列表
      const data = await api.listSchoolTemplates();
      setTemplates(data.templates);
      onSettingsRefreshed?.();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  // ── Loading ──
  if (loading) {
    return (
      <div className="flex items-center gap-3 py-6 text-gray-400 text-sm">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-500" />
        加载学校模板...
      </div>
    );
  }

  // ── Empty ──
  if (templates.length === 0) {
    return (
      <div className="bg-white rounded-xl border p-5 text-center text-gray-400 text-sm">
        暂无学校模板
      </div>
    );
  }

  // ── Helpers for detail rendering ──
  const fs = detail?.format_settings;

  const renderItemRow = (catKey: string) => {
    if (!fs) return null;
    const item = (fs as any)[catKey];
    if (!item?.enabled) return null;

    const parts: string[] = [];
    if (item.font_name) parts.push(item.font_name);
    if (item.font_size_pt) parts.push(ptLabel(item.font_size_pt));
    if (item.bold) parts.push("加粗");
    if (item.alignment && ALIGN_LABELS[item.alignment]) parts.push(ALIGN_LABELS[item.alignment]);
    if (item.line_spacing && item.line_spacing_rule === "EXACTLY") {
      parts.push(`固定值 ${item.line_spacing} 磅`);
    } else if (item.line_spacing && item.line_spacing_rule === "AT_LEAST") {
      parts.push(`最小值 ${item.line_spacing} 磅`);
    } else if (item.line_spacing) {
      parts.push(`${item.line_spacing} 倍行距`);
    }
    if (item.first_line_indent) parts.push(`首行缩进 ${item.first_line_indent}cm`);
    if (item.hanging_indent) parts.push(`悬挂缩进 ${item.hanging_indent}cm`);

    return (
      <div
        key={catKey}
        className="flex items-start gap-2 py-1.5 cursor-pointer hover:bg-gray-50 rounded px-1 -mx-1 transition-colors"
        onClick={() => setExpandedCat(expandedCat === catKey ? null : catKey)}
      >
        <span className="text-[10px] font-medium text-indigo-500 bg-indigo-50 px-1.5 py-0.5 rounded shrink-0 mt-0.5">
          {CATEGORY_NAMES[catKey] || catKey}
        </span>
        <span className="text-xs text-gray-600 leading-relaxed">
          {parts.length > 0 ? parts.join(" · ") : "（已启用）"}
        </span>
        <svg
          className={`w-3 h-3 text-gray-300 shrink-0 mt-0.5 transition-transform ${expandedCat === catKey ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    );
  };

  const renderItemDetail = (catKey: string) => {
    if (!fs || expandedCat !== catKey) return null;
    const item = (fs as any)[catKey];
    if (!item?.enabled) return null;

    const fields: { label: string; value: string }[] = [];
    if (item.font_name) fields.push({ label: "字体", value: item.font_name });
    if (item.font_size_pt) fields.push({ label: "字号", value: `${ptLabel(item.font_size_pt)} (${item.font_size_pt}pt)` });
    if (item.bold !== null) fields.push({ label: "加粗", value: item.bold ? "是" : "否" });
    if (item.alignment) fields.push({ label: "对齐", value: ALIGN_LABELS[item.alignment] || item.alignment });
    if (item.line_spacing) {
      const rule = item.line_spacing_rule === "EXACTLY" ? "固定值" : item.line_spacing_rule === "AT_LEAST" ? "最小值" : "倍行距";
      fields.push({ label: "行距", value: `${rule} ${item.line_spacing}${item.line_spacing_rule === "EXACTLY" || item.line_spacing_rule === "AT_LEAST" ? " 磅" : " 倍"}` });
    }
    if (item.first_line_indent) fields.push({ label: "首行缩进", value: `${item.first_line_indent} cm` });
    if (item.hanging_indent) fields.push({ label: "悬挂缩进", value: `${item.hanging_indent} cm` });
    if (item.space_before) fields.push({ label: "段前", value: `${item.space_before} 磅` });
    if (item.space_after) fields.push({ label: "段后", value: `${item.space_after} 磅` });
    if (item.character_spacing_pt) fields.push({ label: "字符间距", value: `${item.character_spacing_pt} 磅` });

    return (
      <div className="ml-6 mb-2 bg-gray-50 rounded-lg p-3 grid grid-cols-3 gap-1.5 animate-fade-in-up">
        {fields.map((f) => (
          <div key={f.label} className="text-xs">
            <span className="text-gray-400">{f.label}</span>
            <span className="text-gray-700 ml-1 font-medium">{f.value}</span>
          </div>
        ))}
      </div>
    );
  };

  // ── Page settings row ──
  const pageRow = fs?.page?.enabled ? (
    <div
      className="flex items-start gap-2 py-1.5 cursor-pointer hover:bg-gray-50 rounded px-1 -mx-1 transition-colors"
      onClick={() => setExpandedCat(expandedCat === "page" ? null : "page")}
    >
      <span className="text-[10px] font-medium text-emerald-500 bg-emerald-50 px-1.5 py-0.5 rounded shrink-0 mt-0.5">
        页面设置
      </span>
      <span className="text-xs text-gray-600 leading-relaxed">
        上{fs.page.margin_top}cm · 下{fs.page.margin_bottom}cm · 左{fs.page.margin_left}cm · 右{fs.page.margin_right}cm
      </span>
      <svg
        className={`w-3 h-3 text-gray-300 shrink-0 mt-0.5 transition-transform ${expandedCat === "page" ? "rotate-180" : ""}`}
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  ) : null;

  const pageDetail = expandedCat === "page" && fs?.page?.enabled ? (
    <div className="ml-6 mb-2 bg-gray-50 rounded-lg p-3 grid grid-cols-3 gap-1.5 animate-fade-in-up">
      {[
        { label: "上边距", value: fs.page.margin_top },
        { label: "下边距", value: fs.page.margin_bottom },
        { label: "左边距", value: fs.page.margin_left },
        { label: "右边距", value: fs.page.margin_right },
        { label: "纸张", value: fs.page.paper_size },
        { label: "方向", value: fs.page.orientation === "portrait" ? "纵向" : "横向" },
      ].map((f) => (
        <div key={f.label} className="text-xs">
          <span className="text-gray-400">{f.label}</span>
          <span className="text-gray-700 ml-1 font-medium">{f.value}{f.label.includes("边距") ? "cm" : ""}</span>
        </div>
      ))}
    </div>
  ) : null;

  const formatCategories = ["title", "heading_1", "heading_2", "heading_3", "body", "table_caption", "figure_caption", "reference", "toc_title", "toc_entry", "header_footer", "table_text"];

  return (
    <div className="space-y-4 animate-fade-in-up">
      {/* Header + Search */}
      <div className="flex items-center gap-2 flex-wrap">
        <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <h3 className="text-sm font-semibold text-gray-700">学校模板</h3>
        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
          {templates.length} 所
        </span>
        {currentSettings && (
          <button
            onClick={handleSaveCurrent}
            disabled={saving}
            className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-xs font-medium transition-colors disabled:opacity-50"
          >
            {saving ? "保存中..." : "保存当前格式"}
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2.5 text-sm text-red-600 flex items-center justify-between">
          {error}
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600 ml-2">✕</button>
        </div>
      )}

      {/* ── LEVEL 1: School Cards ── */}
      <div className="grid grid-cols-1 gap-3">
        {templates.map((t) => {
          const isSelected = selectedId === t.id;
          return (
            <div key={t.id}>
              <button
                onClick={() => handleSelect(t.id)}
                className={`w-full text-left px-4 py-3.5 rounded-xl border transition-all duration-200 ${
                  isSelected
                    ? "border-indigo-300 bg-indigo-50/60 shadow-sm"
                    : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-800">{t.name}</span>
                      <span className="text-[10px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                        {t.source}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">{cleanDescription(t.description)}</p>
                  </div>
                  <svg
                    className={`w-4 h-4 text-gray-400 shrink-0 transition-transform ${isSelected ? "rotate-180" : ""}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {/* ── LEVEL 2: Expanded Detail ── */}
              {isSelected && (
                <div className="mt-2 ml-2 pl-4 border-l-2 border-indigo-200 space-y-3 animate-fade-in-up">
                  {detailLoading ? (
                    <div className="flex items-center gap-2 py-4 text-gray-400 text-sm">
                      <div className="h-3 w-3 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-500" />
                      加载模板详情...
                    </div>
                  ) : detail ? (
                    <>
                      {/* Format categories */}
                      <div className="bg-white rounded-lg border p-3 space-y-0.5">
                        <p className="text-xs font-medium text-gray-500 mb-2">格式设置一览（点击展开详情）</p>
                        {pageRow}
                        {pageDetail}
                        {formatCategories.map(renderItemRow)}
                        {formatCategories.map(renderItemDetail)}
                      </div>

                      {/* Special rules */}
                      {detail.special_rules.length > 0 && (
                        <div className="bg-amber-50 rounded-lg border border-amber-200 p-3">
                          <p className="text-xs font-medium text-amber-700 mb-1.5">特殊规则</p>
                          <ul className="space-y-0.5">
                            {detail.special_rules.map((rule, i) => (
                              <li key={i} className="text-xs text-amber-800 flex items-start gap-1.5">
                                <span className="text-amber-400 mt-0.5">•</span>
                                {rule}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Extra notes */}
                      {detail.extra_notes && Object.keys(detail.extra_notes).length > 0 && (
                        <div className="bg-blue-50 rounded-lg border border-blue-200 p-3">
                          <p className="text-xs font-medium text-blue-700 mb-1.5">补充说明</p>
                          <ul className="space-y-0.5">
                            {Object.entries(detail.extra_notes).map(([key, val]) => (
                              <li key={key} className="text-xs text-blue-800 flex items-start gap-1.5">
                                <span className="text-blue-400 mt-0.5 font-medium">
                                  {key === "cover" ? "封面" : key === "declaration" ? "作者声明" : key === "page_number" ? "页码" : key}
                                  ：
                                </span>
                                {val}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Apply button */}
                      <button
                        onClick={handleApply}
                        disabled={applying}
                        className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 active:scale-95 transition-all duration-200 shadow-sm hover:shadow-md disabled:opacity-50"
                      >
                        {applying ? "应用中..." : `应用「${detail.name}」模板并重新排版`}
                      </button>
                    </>
                  ) : null}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Success message */}
      {successMsg && (
        <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 border border-green-200 rounded-lg px-4 py-2.5">
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {successMsg}
        </div>
      )}
    </div>
  );
}
