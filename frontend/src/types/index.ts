export type FormatMode = "auto" | "manual"

export type JobStatus =
  | "uploaded"
  | "analyzing"
  | "analyzed"
  | "formatting"
  | "completed"
  | "failed"

export interface FormatJob {
  id: string
  original_filename: string
  file_type: string
  format_mode: FormatMode
  status: JobStatus
  ai_analysis?: string
  output_path: string | null
  price: number
  created_at: string
}

export interface PaperStructure {
  title: string
  abstract: string
  sections: Section[]
  references_count: number
  has_toc: boolean
  has_abstract_section: boolean
}

export interface Section {
  level: number
  title: string
  content_summary: string
  has_figures: boolean
  has_tables: boolean
  start_marker: string
}

export interface ContentMarker {
  type: "table" | "image"
  index: number
  description: string
  rows: number | null
  cols: number | null
  width_px: number | null
  height_px: number | null
}

export interface PreviewSection {
  level: number
  title: string
  content: string[]
  markers: ContentMarker[]
}

export interface PreviewResponse {
  title: string
  section_count: number
  sections: PreviewSection[]
}

export interface FormatSettingItem {
  font_name: string
  font_size: number
  bold: boolean
  alignment: string
  line_spacing: number
  first_line_indent: number
  space_before: number
  space_after: number
}

export interface FormatSettings {
  page_margin_top: number
  page_margin_bottom: number
  page_margin_left: number
  page_margin_right: number
  header_distance: number
  footer_distance: number
  h1: FormatSettingItem
  h2: FormatSettingItem
  h3: FormatSettingItem
  body: FormatSettingItem
  caption: FormatSettingItem
  reference: FormatSettingItem
  header: FormatSettingItem
  footer: FormatSettingItem
  toc_enabled: boolean
  toc_title: FormatSettingItem
  toc_entry: FormatSettingItem
  toc_show_page_numbers: boolean
  toc_page_number_align: string
  toc_include_h3: boolean
}

export interface TemplateInfo {
  id: number
  name: string
  settings: FormatSettings
  created_at: string
}

export interface HistoryRecord {
  jobId: string
  filename: string
  fileType: string
  mode: string
  templateName: string
  timestamp: number
}

export interface AnalysisWarnings {
  missing_abstract: boolean
  missing_toc: boolean
  missing_references: boolean
  missing_figure_labels: string[]
  missing_table_labels: string[]
  conflicting_headings: string[]
}

export const FONT_NAMES = ["宋体", "黑体", "仿宋", "楷体", "Times New Roman", "Arial"] as const

export const FONT_SIZES = [
  { label: "初号 (42pt)", value: 42 },
  { label: "小初 (36pt)", value: 36 },
  { label: "一号 (26pt)", value: 26 },
  { label: "小一 (24pt)", value: 24 },
  { label: "二号 (22pt)", value: 22 },
  { label: "小二 (18pt)", value: 18 },
  { label: "三号 (16pt)", value: 16 },
  { label: "小三 (15pt)", value: 15 },
  { label: "四号 (14pt)", value: 14 },
  { label: "小四 (12pt)", value: 12 },
  { label: "五号 (10.5pt)", value: 10.5 },
  { label: "小五 (9pt)", value: 9 },
] as const

export const DEFAULT_FORMAT_SETTINGS: FormatSettings = {
  page_margin_top: 2.54,
  page_margin_bottom: 2.54,
  page_margin_left: 3.17,
  page_margin_right: 3.17,
  header_distance: 1.5,
  footer_distance: 1.75,
  h1: { font_name: "黑体", font_size: 16, bold: true, alignment: "center", line_spacing: 1.5, first_line_indent: 0, space_before: 12, space_after: 6 },
  h2: { font_name: "黑体", font_size: 14, bold: true, alignment: "left", line_spacing: 1.5, first_line_indent: 0, space_before: 10, space_after: 4 },
  h3: { font_name: "黑体", font_size: 12, bold: true, alignment: "left", line_spacing: 1.5, first_line_indent: 0, space_before: 8, space_after: 4 },
  body: { font_name: "宋体", font_size: 12, bold: false, alignment: "justify", line_spacing: 1.5, first_line_indent: 24, space_before: 0, space_after: 0 },
  caption: { font_name: "宋体", font_size: 10.5, bold: false, alignment: "center", line_spacing: 1.5, first_line_indent: 0, space_before: 2, space_after: 2 },
  reference: { font_name: "宋体", font_size: 10.5, bold: false, alignment: "left", line_spacing: 1.0, first_line_indent: 0, space_before: 0, space_after: 0 },
  header: { font_name: "宋体", font_size: 9, bold: false, alignment: "center", line_spacing: 1.0, first_line_indent: 0, space_before: 0, space_after: 0 },
  footer: { font_name: "宋体", font_size: 9, bold: false, alignment: "center", line_spacing: 1.0, first_line_indent: 0, space_before: 0, space_after: 0 },
  toc_enabled: true,
  toc_title: { font_name: "黑体", font_size: 16, bold: true, alignment: "center", line_spacing: 1.5, first_line_indent: 0, space_before: 0, space_after: 0 },
  toc_entry: { font_name: "宋体", font_size: 12, bold: false, alignment: "left", line_spacing: 1.5, first_line_indent: 0, space_before: 0, space_after: 0 },
  toc_show_page_numbers: true,
  toc_page_number_align: "right",
  toc_include_h3: false,
}

export interface FormatSettingItemEnabled {
  font_name: boolean
  font_size: boolean
  bold: boolean
  alignment: boolean
  line_spacing: boolean
  first_line_indent: boolean
  space_before: boolean
  space_after: boolean
}

export interface FormatSettingsEnabled {
  page_margin_top: boolean
  page_margin_bottom: boolean
  page_margin_left: boolean
  page_margin_right: boolean
  header_distance: boolean
  footer_distance: boolean
  h1: FormatSettingItemEnabled
  h2: FormatSettingItemEnabled
  h3: FormatSettingItemEnabled
  body: FormatSettingItemEnabled
  caption: FormatSettingItemEnabled
  reference: FormatSettingItemEnabled
  header: FormatSettingItemEnabled
  footer: FormatSettingItemEnabled
  toc_title: FormatSettingItemEnabled
  toc_entry: FormatSettingItemEnabled
}

const DEFAULT_ITEM_ENABLED: FormatSettingItemEnabled = {
  font_name: true, font_size: true, bold: true, alignment: true,
  line_spacing: true, first_line_indent: true, space_before: true, space_after: true,
}

export const DEFAULT_ENABLED_SETTINGS: FormatSettingsEnabled = {
  page_margin_top: true, page_margin_bottom: true,
  page_margin_left: true, page_margin_right: true,
  header_distance: true, footer_distance: true,
  h1: { ...DEFAULT_ITEM_ENABLED },
  h2: { ...DEFAULT_ITEM_ENABLED },
  h3: { ...DEFAULT_ITEM_ENABLED },
  body: { ...DEFAULT_ITEM_ENABLED },
  caption: { ...DEFAULT_ITEM_ENABLED },
  reference: { ...DEFAULT_ITEM_ENABLED },
  header: { ...DEFAULT_ITEM_ENABLED },
  footer: { ...DEFAULT_ITEM_ENABLED },
  toc_title: { ...DEFAULT_ITEM_ENABLED },
  toc_entry: { ...DEFAULT_ITEM_ENABLED },
}
