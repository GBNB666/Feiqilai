export interface SectionInfo {
  level: number;
  numbering: string;
  title: string;
  start_marker: string;
  content_summary: string;
  has_figures: boolean;
  has_tables: boolean;
}

export interface StructureOutput {
  title: string;
  subtitle: string | null;
  sections: SectionInfo[];
  has_abstract: boolean;
  has_abstract_en: boolean;
  has_toc: boolean;
  has_references: boolean;
  has_appendix: boolean;
  has_acknowledgement: boolean;
}

export interface FormatWarnings {
  missing_abstract: boolean;
  missing_toc: boolean;
  missing_references: boolean;
  missing_figure_labels: boolean;
  missing_table_labels: boolean;
  conflicting_headings: boolean;
}

export interface JobResponse {
  id: string;
  original_filename: string;
  file_type: string;
  format_mode: string | null;
  status: string;
  price: number;
  created_at: string;
  updated_at: string | null;
  analysis: StructureOutput | null;
  warnings: FormatWarnings | null;
  char_count: number;
  estimated_pages: number;
}

export interface FontInfo {
  font_name: string | null;
  font_size_pt: number | null;
  bold: boolean | null;
  alignment: string | null;
}

export interface BodySample {
  text: string;
  font_info: FontInfo | null;
}

export interface PreviewSection {
  level: number;
  title: string;
  content: string[];
  markers: { type: string; label: string }[];
  is_toc: boolean;
  font_info?: FontInfo | null;
  body_sample?: BodySample | null;
}

export interface PreviewResponse {
  job_id: string;
  title: string;
  sections: PreviewSection[];
  warnings: FormatWarnings | null;
}

export interface TemplateInfo {
  id: number;
  name: string;
  created_at: string;
}

export interface FormatItem {
  enabled: boolean;
  font_name: string | null;
  font_size_pt: number | null;
  bold: boolean | null;
  alignment: string | null;
  line_spacing: number | null;
  line_spacing_rule?: string | null;
  first_line_indent: number | null;
  space_before?: number | null;
  space_after?: number | null;
  character_spacing_pt?: number | null;
  hanging_indent?: number | null;
}

export interface PageSettings {
  enabled: boolean;
  paper_size: string;
  orientation: string;
  margin_top: number;
  margin_bottom: number;
  margin_left: number;
  margin_right: number;
  header_distance: number;
  footer_distance: number;
}

export interface FooterPageNumber {
  enabled: boolean;
  alignment: "LEFT" | "CENTER" | "RIGHT";
}

export interface FormatSettings {
  page: PageSettings;
  title: FormatItem;
  heading_1: FormatItem;
  heading_2: FormatItem;
  heading_3: FormatItem;
  body: FormatItem;
  table_caption: FormatItem;
  figure_caption: FormatItem;
  reference: FormatItem;
  toc_enabled: boolean;
  header_footer: FormatItem;
  toc_title: FormatItem;
  toc_entry: FormatItem;
  table_text: FormatItem;
  footer_page_number: FooterPageNumber;
  latin_font: boolean;
  template?: string;
}

export interface ExtractedImage {
  index: number;
  base64: string;
  width_emu: number;
  height_emu: number;
  content_type: string;
}

export interface ImageExtractResponse {
  job_id: string;
  page_width_usable_emu: number;
  width_ratio_default: number;
  images: ExtractedImage[];
  count: number;
}

export interface SchoolTemplateSummary {
  id: string;
  name: string;
  description: string;
  source: string;
  rule_count: number;
}

export interface SchoolTemplateDetail {
  id: string;
  name: string;
  description: string;
  source: string;
  format_settings: FormatSettings;
  special_rules: string[];
  extra_notes?: Record<string, string>;
}

export type FlowState =
  | "idle"
  | "selecting"
  | "analyzing"
  | "analyzed"
  | "formatting"
  | "done"
  | "error";
