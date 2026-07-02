import { useState, useEffect } from "react";
import type { FormatSettings, FormatItem, PageSettings, FooterPageNumber } from "../../types";

interface Props {
  onApply: (settings: FormatSettings) => void;
}

const FONTS = ["宋体", "黑体", "楷体", "仿宋", "微软雅黑", "Times New Roman", "Arial"];
const FONT_SIZES: { label: string; pt: number }[] = [
  { label: "初号", pt: 42 },
  { label: "小初", pt: 36 },
  { label: "一号", pt: 26 },
  { label: "小一", pt: 24 },
  { label: "二号", pt: 22 },
  { label: "小二", pt: 18 },
  { label: "三号", pt: 16 },
  { label: "小三", pt: 15 },
  { label: "四号", pt: 14 },
  { label: "小四", pt: 12 },
  { label: "五号", pt: 10.5 },
  { label: "小五", pt: 9 },
];
const ALIGNMENTS = [
  { label: "左对齐", value: "LEFT" },
  { label: "居中", value: "CENTER" },
  { label: "右对齐", value: "RIGHT" },
  { label: "两端对齐", value: "JUSTIFY" },
  { label: "分散对齐", value: "DISTRIBUTE" },
];

const LINE_SPACING_RULES = [
  { label: "倍行距", value: "" },
  { label: "固定值", value: "EXACTLY" },
  { label: "最小值", value: "AT_LEAST" },
];

const SAVED_PRESETS_KEY = "paper-formatter-saved-presets";

function ptToLabel(pt: number | null): string {
  if (pt === null || pt === undefined) return "";
  const match = FONT_SIZES.find((s) => Math.abs(s.pt - pt) < 0.01);
  return match ? match.label : "";
}

function makeItem(overrides: Partial<FormatItem> = {}): FormatItem {
  return {
    enabled: false,
    font_name: null,
    font_size_pt: null,
    bold: null,
    alignment: null,
    line_spacing: null,
    line_spacing_rule: null,
    first_line_indent: null,
    space_before: null,
    space_after: null,
    character_spacing_pt: null,
    hanging_indent: null,
    ...overrides,
  };
}

function makeFooterPage(): FooterPageNumber {
  return { enabled: false, alignment: "CENTER" };
}

function makePage(): PageSettings {
  return {
    enabled: false,
    paper_size: "A4",
    orientation: "portrait",
    margin_top: 2.54,
    margin_bottom: 2.54,
    margin_left: 3.17,
    margin_right: 3.17,
    header_distance: 1.5,
    footer_distance: 1.75,
  };
}

const TEMPLATES: Record<string, FormatSettings> = {
  academic: {
    page: makePage(),
    title: makeItem({ font_name: "黑体", font_size_pt: 22, bold: true, alignment: "CENTER" }),
    heading_1: makeItem({ font_name: "黑体", font_size_pt: 16, bold: true, alignment: "CENTER" }),
    heading_2: makeItem({ font_name: "黑体", font_size_pt: 14, bold: true, alignment: "LEFT" }),
    heading_3: makeItem({ font_name: "黑体", font_size_pt: 12, bold: true, alignment: "LEFT" }),
    body: makeItem({ font_name: "宋体", font_size_pt: 12, alignment: "JUSTIFY", line_spacing: 1.5, first_line_indent: 0.74 }),
    table_caption: makeItem({ font_name: "宋体", font_size_pt: 10.5, alignment: "CENTER" }),
    figure_caption: makeItem({ font_name: "宋体", font_size_pt: 10.5, alignment: "CENTER" }),
    reference: makeItem({ font_name: "宋体", font_size_pt: 10.5, alignment: "LEFT", line_spacing: 1.0, hanging_indent: 0.74 }),
    header_footer: makeItem({ font_name: "宋体", font_size_pt: 9, alignment: "CENTER" }),
    toc_title: makeItem({ font_name: "黑体", font_size_pt: 16, bold: true, alignment: "CENTER" }),
    toc_entry: makeItem({ font_name: "宋体", font_size_pt: 12, alignment: "LEFT", line_spacing: 1.5 }),
    table_text: makeItem({ font_name: "宋体", font_size_pt: 10.5 }),
    footer_page_number: makeFooterPage(),
    latin_font: true,
    toc_enabled: false,
    template: "academic",
  },
  business: {
    page: { enabled: true, paper_size: "A4", orientation: "portrait", margin_top: 2.54, margin_bottom: 2.54, margin_left: 3.17, margin_right: 3.17, header_distance: 1.5, footer_distance: 1.75 },
    title: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 22, bold: true, alignment: "CENTER" }),
    heading_1: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 16, bold: true, alignment: "CENTER" }),
    heading_2: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 15, bold: true, alignment: "LEFT" }),
    heading_3: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 14, bold: true, alignment: "LEFT", first_line_indent: 0.74 }),
    body: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 12, alignment: "JUSTIFY", line_spacing: 1.5, first_line_indent: 0.74 }),
    table_caption: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 10.5, bold: true, alignment: "CENTER", space_after: 6 }),
    figure_caption: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 10.5, bold: true, alignment: "CENTER", space_before: 6 }),
    reference: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 10.5, alignment: "LEFT", line_spacing: 1.0, hanging_indent: 0.74 }),
    header_footer: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 9, alignment: "CENTER" }),
    toc_title: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 16, bold: true, alignment: "CENTER" }),
    toc_entry: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 12, alignment: "LEFT", line_spacing: 1.5 }),
    table_text: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 10.5 }),
    footer_page_number: makeFooterPage(),
    latin_font: true,
    toc_enabled: false,
    template: "business",
  },
  competition: {
    page: { enabled: true, paper_size: "A4", orientation: "portrait", margin_top: 2.4, margin_bottom: 2.0, margin_left: 2.4, margin_right: 2.4, header_distance: 1.5, footer_distance: 1.75 },
    title: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 22 }),
    heading_1: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 18, bold: true, space_before: 9, space_after: 9 }),
    heading_2: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 16, bold: true, space_before: 8, space_after: 8 }),
    heading_3: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 14, bold: true }),
    body: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 14, alignment: "JUSTIFY", line_spacing: 22, line_spacing_rule: "AT_LEAST" }),
    table_caption: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 10.5, bold: true, alignment: "CENTER", space_after: 6 }),
    figure_caption: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 10.5, bold: true, alignment: "CENTER", space_before: 6 }),
    reference: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 10.5, alignment: "LEFT", line_spacing: 1.0, hanging_indent: 0.74 }),
    header_footer: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 9, alignment: "CENTER" }),
    toc_title: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 14 }),
    toc_entry: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 14 }),
    table_text: makeItem({ enabled: true, font_name: "楷体", font_size_pt: 10.5 }),
    footer_page_number: makeFooterPage(),
    latin_font: true,
    toc_enabled: false,
    template: "competition",
  },
  medicine: {
    page: { enabled: true, paper_size: "A4", orientation: "portrait", margin_top: 3.0, margin_bottom: 2.5, margin_left: 3.0, margin_right: 2.5, header_distance: 1.5, footer_distance: 1.75 },
    title: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 22, bold: true, alignment: "CENTER" }),
    heading_1: makeItem({ enabled: true, font_name: "黑体", font_size_pt: 14, bold: true, alignment: "LEFT" }),
    heading_2: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 14, bold: true, alignment: "LEFT" }),
    heading_3: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 12, bold: true, alignment: "LEFT" }),
    body: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 12, alignment: "JUSTIFY", line_spacing: 22, line_spacing_rule: "EXACTLY", first_line_indent: 0.74 }),
    table_caption: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 10.5, alignment: "CENTER", space_after: 6 }),
    figure_caption: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 10.5, alignment: "CENTER", space_before: 6 }),
    reference: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 10.5, alignment: "LEFT", hanging_indent: 0.74 }),
    header_footer: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 9, alignment: "CENTER" }),
    toc_title: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 18, bold: true, alignment: "CENTER", space_before: 12, space_after: 12 }),
    toc_entry: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 12, alignment: "LEFT", line_spacing: 22, line_spacing_rule: "EXACTLY" }),
    table_text: makeItem({ enabled: true, font_name: "宋体", font_size_pt: 10.5 }),
    footer_page_number: makeFooterPage(),
    latin_font: true,
    toc_enabled: false,
    template: "medicine",
  },
};

const BUILTIN_KEYS = ["academic", "business", "competition", "medicine"];
const BUILTIN_LABELS: Record<string, string> = {
  academic: "学术论文",
  business: "商业计划书",
  competition: "创业计划大赛",
  medicine: "医学院论文",
};

function loadSavedPresets(): Record<string, FormatSettings> {
  try {
    const raw = localStorage.getItem(SAVED_PRESETS_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* localStorage unavailable */ }
  return {};
}

function savePresetsToStorage(presets: Record<string, FormatSettings>) {
  try {
    localStorage.setItem(SAVED_PRESETS_KEY, JSON.stringify(presets));
  } catch { /* localStorage unavailable */ }
}

const DEFAULT_TEMPLATE_KEY = "paper-formatter-default-template";

function getDefaultTemplateKey(): string {
  try {
    const raw = localStorage.getItem(DEFAULT_TEMPLATE_KEY);
    if (raw) {
      if (BUILTIN_KEYS.includes(raw)) return raw;
      const saved = loadSavedPresets();
      if (raw in saved) return raw;
    }
  } catch {}
  return "academic";
}

function setDefaultTemplateKey(name: string) {
  try { localStorage.setItem(DEFAULT_TEMPLATE_KEY, name); } catch {}
}

export default function FormatSettingsPanel({ onApply }: Props) {
  const defaultKey = getDefaultTemplateKey();
  const initTemplate = TEMPLATES[defaultKey] || TEMPLATES.academic;
  const [settings, setSettings] = useState<FormatSettings>(initTemplate);
  const [templateName, setTemplateName] = useState(defaultKey);
  const [defaultTemplate, setDefaultTemplate] = useState(defaultKey);
  const [savedPresets, setSavedPresets] = useState<Record<string, FormatSettings>>({});
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [presetName, setPresetName] = useState("");
  const [nameError, setNameError] = useState("");

  useEffect(() => {
    setSavedPresets(loadSavedPresets());
  }, []);

  const presetNames = Object.keys(savedPresets);
  const isUserPreset = presetNames.includes(templateName);
  const isDefault = templateName === defaultTemplate;

  const handleSetDefault = () => {
    setDefaultTemplateKey(templateName);
    setDefaultTemplate(templateName);
  };

  const handleTemplateChange = (name: string) => {
    setTemplateName(name);
    setNameError("");

    if (BUILTIN_KEYS.includes(name)) {
      setSettings({ ...TEMPLATES[name] });
    } else {
      const preset = savedPresets[name];
      if (preset) {
        setSettings({ ...preset, template: name });
      }
    }
  };

  const handleSavePreset = () => {
    const name = presetName.trim();
    if (!name) {
      setNameError("请输入名称");
      return;
    }
    if (BUILTIN_KEYS.includes(name)) {
      setNameError("不能与内置模板同名");
      return;
    }
    const updated = { ...savedPresets, [name]: { ...settings, template: name } };
    setSavedPresets(updated);
    savePresetsToStorage(updated);
    setTemplateName(name);
    setShowSaveDialog(false);
    setPresetName("");
    setNameError("");
  };

  const handleDeletePreset = (name: string) => {
    const updated = { ...savedPresets };
    delete updated[name];
    setSavedPresets(updated);
    savePresetsToStorage(updated);
    if (templateName === name) {
      setTemplateName("academic");
      setSettings({ ...TEMPLATES.academic });
    }
  };

  const updatePage = (field: string, value: any) => {
    setSettings((prev) => ({
      ...prev,
      page: { ...prev.page, [field]: value, enabled: true },
    }));
  };

  const updateItem = (key: string, field: string, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [key]: { ...(prev as any)[key], [field]: value, enabled: true },
    }));
  };

  const toggleEnabled = (key: string) => {
    if (key === "page") {
      setSettings((prev) => ({
        ...prev,
        page: { ...prev.page, enabled: !prev.page.enabled },
      }));
    } else {
      setSettings((prev) => ({
        ...prev,
        [key]: { ...(prev as any)[key], enabled: !(prev as any)[key].enabled },
      }));
    }
  };

  const handleApply = () => {
    onApply(settings);
  };

  return (
    <div className="space-y-3">
      {/* ── 顶部：模板选择 + 操作按钮 ── */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-700">自定义格式</h3>
          <select
            value={templateName}
            onChange={(e) => handleTemplateChange(e.target.value)}
            className="text-xs border rounded px-2 py-1 bg-white text-gray-600"
          >
            <optgroup label="内置模板">
              {BUILTIN_KEYS.map((key) => (
                <option key={key} value={key}>{BUILTIN_LABELS[key]}</option>
              ))}
            </optgroup>
            {presetNames.length > 0 && (
              <optgroup label="我的模板">
                {presetNames.map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </optgroup>
            )}
          </select>
          {isDefault && (
            <span className="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">默认</span>
          )}
          {isUserPreset && (
            <span className="text-xs text-indigo-500 bg-indigo-50 px-1.5 py-0.5 rounded font-medium">我的</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!isDefault && (
            <button
              onClick={handleSetDefault}
              className="px-3 py-1.5 bg-amber-500 text-white rounded-lg hover:bg-amber-600 text-xs font-medium transition-colors"
              title="下次打开自动加载此模板"
            >
              设为默认
            </button>
          )}
          <button
            onClick={() => {
              setShowSaveDialog(true);
              setPresetName("");
              setNameError("");
            }}
            className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-xs font-medium transition-colors"
          >
            保存为模板
          </button>
          {isUserPreset && (
            <button
              onClick={() => handleDeletePreset(templateName)}
              className="px-2 py-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 rounded text-xs font-medium transition-colors"
              title={`删除「${templateName}」`}
            >
              删除
            </button>
          )}
          <button
            onClick={handleApply}
            className="px-4 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-xs font-medium transition-colors"
          >
            应用设置
          </button>
        </div>
      </div>

      {/* ── 保存弹窗 ── */}
      {showSaveDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="bg-white rounded-xl shadow-xl p-5 w-80 animate-fade-in-up">
            <h4 className="text-sm font-semibold text-gray-800 mb-3">保存为我的模板</h4>
            <input
              type="text"
              value={presetName}
              onChange={(e) => { setPresetName(e.target.value); setNameError(""); }}
              placeholder="输入模板名称…"
              className="w-full text-sm border rounded-lg px-3 py-2 mb-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && handleSavePreset()}
            />
            {nameError && <p className="text-xs text-red-500 mb-2">{nameError}</p>}
            <div className="flex justify-end gap-2 mt-3">
              <button
                onClick={() => setShowSaveDialog(false)}
                className="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSavePreset}
                className="px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                确认保存
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── 格式项列表 ── */}
      <div className="border rounded-lg bg-white divide-y divide-gray-100">
        <PageSettingsRow page={settings.page} onToggle={() => toggleEnabled("page")} onChange={updatePage} />

        <FormatRow label="论文标题"     item={settings.title}        onToggle={() => toggleEnabled("title")}        onChange={(f, v) => updateItem("title", f, v)} />
        <FormatRow label="一级标题"     item={settings.heading_1}    onToggle={() => toggleEnabled("heading_1")}    onChange={(f, v) => updateItem("heading_1", f, v)} />
        <FormatRow label="二级标题"     item={settings.heading_2}    onToggle={() => toggleEnabled("heading_2")}    onChange={(f, v) => updateItem("heading_2", f, v)} />
        <FormatRow label="三级标题"     item={settings.heading_3}    onToggle={() => toggleEnabled("heading_3")}    onChange={(f, v) => updateItem("heading_3", f, v)} />
        <FormatRow label="正文"         item={settings.body}         onToggle={() => toggleEnabled("body")}         onChange={(f, v) => updateItem("body", f, v)} showIndent showLineSpacing showParaSpacing showCharSpacing />
        <FormatRow label="表注"         item={settings.table_caption}  onToggle={() => toggleEnabled("table_caption")}  onChange={(f, v) => updateItem("table_caption", f, v)} showParaSpacing />
        <FormatRow label="图注"         item={settings.figure_caption} onToggle={() => toggleEnabled("figure_caption")} onChange={(f, v) => updateItem("figure_caption", f, v)} showParaSpacing />
        <FormatRow label="表格文字"     item={settings.table_text}   onToggle={() => toggleEnabled("table_text")}   onChange={(f, v) => updateItem("table_text", f, v)} />
        <FormatRow label="参考文献条目" item={settings.reference}    onToggle={() => toggleEnabled("reference")}    onChange={(f, v) => updateItem("reference", f, v)} showLineSpacing showHangingIndent />
        <FormatRow label="页眉/页脚"    item={settings.header_footer} onToggle={() => toggleEnabled("header_footer")} onChange={(f, v) => updateItem("header_footer", f, v)} />

        <FormatRow label="目录标题"     item={settings.toc_title}    onToggle={() => toggleEnabled("toc_title")}    onChange={(f, v) => updateItem("toc_title", f, v)} />
        <FormatRow label="目录条目"     item={settings.toc_entry}    onToggle={() => toggleEnabled("toc_entry")}    onChange={(f, v) => updateItem("toc_entry", f, v)} showLineSpacing />

        {/* TOC enabled toggle */}
        <div className="px-4 py-2.5 border-t border-gray-100">
          <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              className="w-4 h-4 rounded"
              checked={settings.toc_enabled}
              onChange={(e) => setSettings((p) => ({ ...p, toc_enabled: e.target.checked }))}
            />
            <span className="font-medium">生成目录</span>
            <span className="text-xs text-gray-400">（在文档开头插入带页码的目录，Word 打开即自动更新）</span>
          </label>
        </div>

        {/* Footer page number */}
        <div className="px-4 py-3 border-t border-gray-100">
          <label className="flex items-center gap-2 cursor-pointer mb-2">
            <input
              type="checkbox"
              className="w-4 h-4 rounded"
              checked={settings.footer_page_number?.enabled || false}
              onChange={(e) =>
                setSettings((p) => ({
                  ...p,
                  footer_page_number: { ...(p.footer_page_number || { enabled: false, alignment: "CENTER" }), enabled: e.target.checked },
                }))
              }
            />
            <span className="text-sm font-medium text-gray-800">是否显示 页脚页码</span>
          </label>
          {settings.footer_page_number?.enabled && (
            <div className="ml-6 flex items-center gap-2">
              <span className="text-xs text-gray-400">对齐</span>
              <select
                value={settings.footer_page_number?.alignment || "CENTER"}
                onChange={(e) =>
                  setSettings((p) => ({
                    ...p,
                    footer_page_number: { ...(p.footer_page_number || { enabled: true, alignment: "CENTER" }), alignment: e.target.value as "LEFT" | "CENTER" | "RIGHT" },
                  }))
                }
                className="text-xs border rounded px-1.5 py-0.5 bg-white"
              >
                <option value="LEFT">左对齐</option>
                <option value="CENTER">居中</option>
                <option value="RIGHT">右对齐</option>
              </select>
            </div>
          )}
        </div>

        {/* Latin Font toggle */}
        <div className="px-4 py-2.5 border-t border-gray-100">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              className="w-4 h-4 rounded"
              checked={settings.latin_font}
              onChange={(e) => setSettings((p) => ({ ...p, latin_font: e.target.checked }))}
            />
            西文使用 Times New Roman
          </label>
        </div>
      </div>
    </div>
  );
}

function PageSettingsRow({
  page,
  onToggle,
  onChange,
}: {
  page: PageSettings;
  onToggle: () => void;
  onChange: (field: string, value: any) => void;
}) {
  const disabled = !page.enabled;
  return (
    <div className={`px-4 py-3 ${disabled ? "opacity-50" : ""}`}>
      <label className="flex items-center gap-2 cursor-pointer mb-2">
        <input type="checkbox" className="w-4 h-4 rounded" checked={page.enabled} onChange={onToggle} />
        <span className="text-sm font-medium text-gray-800">是否更改 页面设置</span>
      </label>
      <div className="grid grid-cols-3 gap-2 ml-6">
        <NumberField label="上边距(cm)" value={page.margin_top} onChange={(v) => onChange("margin_top", v)} disabled={disabled} />
        <NumberField label="下边距(cm)" value={page.margin_bottom} onChange={(v) => onChange("margin_bottom", v)} disabled={disabled} />
        <NumberField label="左边距(cm)" value={page.margin_left} onChange={(v) => onChange("margin_left", v)} disabled={disabled} />
        <NumberField label="右边距(cm)" value={page.margin_right} onChange={(v) => onChange("margin_right", v)} disabled={disabled} />
        <NumberField label="页眉距(cm)" value={page.header_distance} onChange={(v) => onChange("header_distance", v)} disabled={disabled} />
        <NumberField label="页脚距(cm)" value={page.footer_distance} onChange={(v) => onChange("footer_distance", v)} disabled={disabled} />
      </div>
    </div>
  );
}

function FormatRow({
  label,
  item,
  onToggle,
  onChange,
  showIndent = false,
  showLineSpacing = false,
  showParaSpacing = false,
  showCharSpacing = false,
  showHangingIndent = false,
}: {
  label: string;
  item: FormatItem;
  onToggle: () => void;
  onChange: (field: string, value: any) => void;
  showIndent?: boolean;
  showLineSpacing?: boolean;
  showParaSpacing?: boolean;
  showCharSpacing?: boolean;
  showHangingIndent?: boolean;
}) {
  const disabled = !item.enabled;
  return (
    <div className={`px-4 py-3 ${disabled ? "opacity-50" : ""}`}>
      <label className="flex items-center gap-2 cursor-pointer mb-2">
        <input type="checkbox" className="w-4 h-4 rounded" checked={item.enabled} onChange={onToggle} />
        <span className="text-sm font-medium text-gray-800">是否更改 {label}</span>
      </label>
      <div className="flex flex-wrap items-center gap-2 ml-6">
        <SelectField
          label="字体"
          value={item.font_name || ""}
          options={FONTS.map((f) => ({ label: f, value: f }))}
          onChange={(v) => onChange("font_name", v || null)}
          disabled={disabled}
        />
        <SelectField
          label="字号"
          value={ptToLabel(item.font_size_pt)}
          options={FONT_SIZES.map((s) => ({ label: s.label, value: s.label }))}
          onChange={(v) => {
            const sz = FONT_SIZES.find((s) => s.label === v);
            onChange("font_size_pt", sz ? sz.pt : null);
          }}
          disabled={disabled}
        />
        <label className="flex items-center gap-1 text-xs text-gray-500 cursor-pointer">
          <input
            type="checkbox"
            className="w-3.5 h-3.5"
            checked={!!item.bold}
            disabled={disabled}
            onChange={(e) => onChange("bold", e.target.checked || null)}
          />
          加粗
        </label>
        <SelectField
          label="对齐"
          value={item.alignment || ""}
          options={ALIGNMENTS}
          onChange={(v) => onChange("alignment", v || null)}
          disabled={disabled}
        />
        {showLineSpacing && (
          <>
            <NumberField
              label="行距"
              value={item.line_spacing ?? 1.5}
              onChange={(v) => onChange("line_spacing", v)}
              disabled={disabled}
              step={0.25}
            />
            <SelectField
              label="行距模式"
              value={item.line_spacing_rule || ""}
              options={LINE_SPACING_RULES}
              onChange={(v) => onChange("line_spacing_rule", v || null)}
              disabled={disabled}
            />
          </>
        )}
        {showParaSpacing && (
          <>
            <NumberField
              label="段前(磅)"
              value={item.space_before ?? 0}
              onChange={(v) => onChange("space_before", v)}
              disabled={disabled}
              step={1}
            />
            <NumberField
              label="段后(磅)"
              value={item.space_after ?? 0}
              onChange={(v) => onChange("space_after", v)}
              disabled={disabled}
              step={1}
            />
          </>
        )}
        {showCharSpacing && (
          <NumberField
            label="字间距(磅)"
            value={item.character_spacing_pt ?? 0}
            onChange={(v) => onChange("character_spacing_pt", v)}
            disabled={disabled}
            step={0.1}
          />
        )}
        {showIndent && (
          <NumberField
            label="首行缩进(cm)"
            value={item.first_line_indent ?? 0.74}
            onChange={(v) => onChange("first_line_indent", v)}
            disabled={disabled}
            step={0.1}
          />
        )}
        {showHangingIndent && (
          <NumberField
            label="悬挂缩进(cm)"
            value={item.hanging_indent ?? 0.74}
            onChange={(v) => onChange("hanging_indent", v)}
            disabled={disabled}
            step={0.1}
          />
        )}
      </div>
    </div>
  );
}

function SelectField({
  label,
  value,
  options,
  onChange,
  disabled,
}: {
  label: string;
  value: string;
  options: { label: string; value: string }[];
  onChange: (v: string) => void;
  disabled: boolean;
}) {
  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-gray-400">{label}</span>
      <select
        className="text-xs border rounded px-1.5 py-0.5 bg-white disabled:bg-gray-100"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        <option value="">默认</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function NumberField({
  label,
  value,
  onChange,
  disabled,
  step = 0.1,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
  step?: number;
}) {
  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-gray-400">{label}</span>
      <input
        type="number"
        className="text-xs border rounded px-1.5 py-0.5 w-16 text-center disabled:bg-gray-100"
        value={value}
        step={step}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
        disabled={disabled}
      />
    </div>
  );
}
