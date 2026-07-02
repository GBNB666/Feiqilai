from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────

class JobStatus(str, Enum):
    UPLOADED = "UPLOADED"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FORMATTING = "FORMATTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FormatMode(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"


# ── AI Structure ────────────────────────────────────

class SectionInfo(BaseModel):
    level: int
    numbering: str = ""
    title: str = ""
    start_marker: str = ""
    content_summary: str = ""
    has_figures: bool = False
    has_tables: bool = False


class StructureOutput(BaseModel):
    title: str = ""
    subtitle: str | None = None
    sections: list[SectionInfo] = []
    has_abstract: bool = False
    has_abstract_en: bool = False
    has_toc: bool = False
    has_references: bool = False
    has_appendix: bool = False
    has_acknowledgement: bool = False


# ── Format Settings ─────────────────────────────────

class PageSettingsModel(BaseModel):
    enabled: bool = False
    paper_size: str = "A4"
    orientation: str = "portrait"
    margin_top: float = 2.54
    margin_bottom: float = 2.54
    margin_left: float = 3.17
    margin_right: float = 3.17
    header_distance: float = 1.5
    footer_distance: float = 1.75


class FormatItemModel(BaseModel):
    enabled: bool = False
    font_name: str | None = None
    font_size_pt: float | None = None
    bold: bool | None = None
    alignment: str | None = None
    line_spacing: float | None = None
    line_spacing_rule: str | None = None
    first_line_indent: float | None = None
    space_before: float | None = None
    space_after: float | None = None
    character_spacing_pt: float | None = None
    hanging_indent: float | None = None


class FooterPageNumberModel(BaseModel):
    enabled: bool = False
    alignment: str = "CENTER"  # LEFT | CENTER | RIGHT


class FormatSettingsModel(BaseModel):
    page: PageSettingsModel = Field(default_factory=PageSettingsModel)
    title: FormatItemModel = Field(default_factory=FormatItemModel)
    heading_1: FormatItemModel = Field(default_factory=FormatItemModel)
    heading_2: FormatItemModel = Field(default_factory=FormatItemModel)
    heading_3: FormatItemModel = Field(default_factory=FormatItemModel)
    body: FormatItemModel = Field(default_factory=FormatItemModel)
    table_caption: FormatItemModel = Field(default_factory=FormatItemModel)
    figure_caption: FormatItemModel = Field(default_factory=FormatItemModel)
    reference: FormatItemModel = Field(default_factory=FormatItemModel)
    toc_enabled: bool = False
    header_footer: FormatItemModel = Field(default_factory=FormatItemModel)
    toc_title: FormatItemModel = Field(default_factory=FormatItemModel)
    toc_entry: FormatItemModel = Field(default_factory=FormatItemModel)
    table_text: FormatItemModel = Field(default_factory=FormatItemModel)
    footer_page_number: FooterPageNumberModel = Field(default_factory=FooterPageNumberModel)
    latin_font: bool = True
    template: str = "academic"


# ── Warnings ────────────────────────────────────────

class FormatWarnings(BaseModel):
    missing_abstract: bool = False
    missing_toc: bool = False
    missing_references: bool = False
    missing_figure_labels: bool = False
    missing_table_labels: bool = False
    conflicting_headings: bool = False


# ── Job ─────────────────────────────────────────────

class JobResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    format_mode: str | None = None
    status: JobStatus
    price: float = 9.9
    created_at: datetime
    updated_at: datetime | None = None
    analysis: StructureOutput | None = None
    warnings: FormatWarnings | None = None
    char_count: int = 0
    estimated_pages: int = 0

    model_config = {"from_attributes": True}


class SelectModeRequest(BaseModel):
    job_id: str
    format_mode: FormatMode


class AnnotationItem(BaseModel):
    section_index: int
    field: str
    value: str


class AnnotationsPayload(BaseModel):
    job_id: str
    annotations: list[AnnotationItem] = []


class CustomizePayload(BaseModel):
    job_id: str
    settings: FormatSettingsModel | None = None


class ModifySectionPayload(BaseModel):
    job_id: str
    section_index: int
    new_content: str


# ── Preview ─────────────────────────────────────────

class ContentMarker(BaseModel):
    type: str  # "image" | "table" | "toc"
    label: str = ""


class FontInfo(BaseModel):
    font_name: str | None = None
    font_size_pt: float | None = None
    bold: bool | None = None
    alignment: str | None = None


class BodySample(BaseModel):
    text: str = ""
    font_info: FontInfo | None = None


class SectionPreview(BaseModel):
    level: int
    title: str = ""
    content: list[str] = []
    markers: list[ContentMarker] = []
    is_toc: bool = False
    font_info: FontInfo | None = None
    body_sample: BodySample | None = None


class PreviewResponse(BaseModel):
    job_id: str
    title: str = ""
    sections: list[SectionPreview] = []
    warnings: FormatWarnings | None = None


# ── Template ────────────────────────────────────────

class TemplateResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateSaveRequest(BaseModel):
    name: str
    settings_json: str


# ── Image Extraction ────────────────────────────────

class ExtractedImage(BaseModel):
    index: int
    base64: str
    width_emu: int
    height_emu: int
    content_type: str = "image/png"


class ImageExtractResponse(BaseModel):
    job_id: str
    page_width_usable_emu: int
    width_ratio_default: float = 0.7
    images: list[ExtractedImage] = []
    count: int


# ── Generic ─────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: str = ""


class HealthResponse(BaseModel):
    status: str = "ok"
