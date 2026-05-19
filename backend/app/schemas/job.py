from pydantic import BaseModel
from datetime import datetime


class JobResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    format_mode: str
    status: str
    ai_analysis: str | None = None
    output_path: str | None = None
    price: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ModeSelectRequest(BaseModel):
    job_id: str
    format_mode: str


class AnnotationRequest(BaseModel):
    job_id: str
    annotations: str


class ContentMarker(BaseModel):
    type: str  # "table" | "image"
    index: int
    description: str
    rows: int | None = None
    cols: int | None = None
    width_px: int | None = None
    height_px: int | None = None


class PreviewSection(BaseModel):
    level: int
    title: str
    content: str
    markers: list[ContentMarker] = []


class PreviewResponse(BaseModel):
    title: str
    section_count: int
    sections: list[PreviewSection]


class FormatSettingItem(BaseModel):
    font_name: str = ""
    font_size: float = 0  # pt
    bold: bool = False
    alignment: str = ""  # left/center/right/justify
    line_spacing: float = 0
    first_line_indent: int = 0  # pt
    space_before: int = 0  # pt
    space_after: int = 0  # pt


class FormatSettings(BaseModel):
    page_margin_top: float = 2.54
    page_margin_bottom: float = 2.54
    page_margin_left: float = 3.17
    page_margin_right: float = 3.17
    header_distance: float = 1.5
    footer_distance: float = 1.75
    h1: FormatSettingItem = FormatSettingItem(font_name="黑体", font_size=16, bold=True, alignment="center", line_spacing=1.5)
    h2: FormatSettingItem = FormatSettingItem(font_name="黑体", font_size=14, bold=True, alignment="left", line_spacing=1.5)
    h3: FormatSettingItem = FormatSettingItem(font_name="黑体", font_size=12, bold=True, alignment="left", line_spacing=1.5)
    body: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=12, bold=False, alignment="justify", line_spacing=1.5, first_line_indent=24)
    caption: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=10.5, bold=False, alignment="center", line_spacing=1.5)
    reference: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=10.5, bold=False, alignment="left", line_spacing=1.0)
    header: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=9, bold=False, alignment="center")
    footer: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=9, bold=False, alignment="center")
    toc_enabled: bool = True
    toc_title: FormatSettingItem = FormatSettingItem(font_name="黑体", font_size=16, bold=True, alignment="center", line_spacing=1.5)
    toc_entry: FormatSettingItem = FormatSettingItem(font_name="宋体", font_size=12, bold=False, alignment="left", line_spacing=1.5)
    toc_show_page_numbers: bool = True
    toc_page_number_align: str = "right"
    toc_include_h3: bool = False


class FormatSettingItemEnabled(BaseModel):
    font_name: bool = True
    font_size: bool = True
    bold: bool = True
    alignment: bool = True
    line_spacing: bool = True
    first_line_indent: bool = True
    space_before: bool = True
    space_after: bool = True


class FormatSettingsEnabled(BaseModel):
    page_margin_top: bool = True
    page_margin_bottom: bool = True
    page_margin_left: bool = True
    page_margin_right: bool = True
    header_distance: bool = True
    footer_distance: bool = True
    h1: FormatSettingItemEnabled = FormatSettingItemEnabled()
    h2: FormatSettingItemEnabled = FormatSettingItemEnabled()
    h3: FormatSettingItemEnabled = FormatSettingItemEnabled()
    body: FormatSettingItemEnabled = FormatSettingItemEnabled()
    caption: FormatSettingItemEnabled = FormatSettingItemEnabled()
    reference: FormatSettingItemEnabled = FormatSettingItemEnabled()
    header: FormatSettingItemEnabled = FormatSettingItemEnabled()
    footer: FormatSettingItemEnabled = FormatSettingItemEnabled()
    toc_title: FormatSettingItemEnabled = FormatSettingItemEnabled()
    toc_entry: FormatSettingItemEnabled = FormatSettingItemEnabled()


class CustomizeRequest(BaseModel):
    job_id: str
    settings: FormatSettings
    enabled: FormatSettingsEnabled | None = None


class ModifySectionRequest(BaseModel):
    job_id: str
    section_index: int  # 0-based
    new_content: str


class TemplateSaveRequest(BaseModel):
    name: str
    settings: FormatSettings


class TemplateResponse(BaseModel):
    id: int
    name: str
    settings: FormatSettings
    created_at: str


class AnalysisWarnings(BaseModel):
    missing_abstract: bool = False
    missing_toc: bool = False
    missing_references: bool = False
    missing_figure_labels: list[str] = []
    missing_table_labels: list[str] = []
    conflicting_headings: list[str] = []
