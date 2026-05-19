# Paper-Formatter V2 设计文档

## 项目目标

一个论文AI格式排版网站。用户上传docx/pdf论文 → AI分析结构 → 按护理学论文学术规范自动排版 → 下载修正后的文件。

**成功标准**：上传一篇格式打乱的论文，排版后下载结果，与标准格式论文对比——标题层级、字体、字号、行距、缩进、对齐全部一致。

**失败/不该做的**：支付、用户登录、CDN部署、真实页码计算（本轮不做）。

---

## 一、技术栈

| 层 | 技术 |
|----|------|
| 后端框架 | Python + FastAPI |
| 数据库 | SQLite + SQLAlchemy |
| 文档处理 | python-docx (DOCX), PyPDF2 (PDF提取) |
| AI | DeepSeek-V4 API (response_format=json_object) |
| 前端 | React 19 + TypeScript + Vite 8 + Tailwind CSS 4 + shadcn/ui |

---

## 二、板块架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    大框架：FastAPI + React                 │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ 1.文件    │  │ 2.AI分析  │  │ 3.排版    │  │ 4.格式    │ │
│  │   处理    │→│   引擎    │→│   引擎    │←│   标准    │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│       │              │              │              │      │
│       └──────────────┴──────────────┴──────────────┘      │
│                          │                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ 5.预览    │  │ 6.任务    │  │ 7.模板    │  │ 8.前端    │ │
│  │   服务    │  │   管理    │  │   管理    │  │   UI     │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              9.基础设施（配置/数据库/API路由）      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 依赖方向（严格单向，右依赖左）

```
9(基础设施) ← 1(文件处理) ← 2(AI分析) ← 3(排版引擎) ← 5(预览)
    ↑              ↑                          ↑
6(任务管理)   7(模板管理)                  4(格式标准)
```

---

## 三、后端目录结构

```
backend/
├── app/
│   ├── main.py              ← 框架入口：创建FastAPI、注册路由、初始化DB
│   ├── config.py             ← 配置中心（板块9）
│   ├── database.py           ← 数据库引擎（板块9）
│   │
│   ├── modules/              ← 各板块独立目录
│   │   ├── file_handler/     ← 板块1：文件处理
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← /api/upload, /api/download
│   │   │   ├── service.py    ← 验证、存储
│   │   │   └── extractors.py ← DOCX/PDF文本提取
│   │   │
│   │   ├── ai_analyzer/      ← 板块2：AI分析
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← /api/format/analyze
│   │   │   ├── service.py    ← DeepSeek调用、结构解析
│   │   │   ├── prompt.py     ← SYSTEM_PROMPT
│   │   │   └── warnings.py   ← 格式警告检测
│   │   │
│   │   ├── format_engine/    ← 板块3：排版引擎
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← /api/format/execute, /api/format/customize, /api/format/annotate, /api/format/modify-section
│   │   │   ├── service.py    ← 排版编排器
│   │   │   ├── matcher.py    ← 段落→章节匹配（预览也复用此模块）
│   │   │   ├── applier.py    ← 格式应用
│   │   │   └── toc.py        ← 目录生成
│   │   │
│   │   ├── format_standards/ ← 板块4：格式标准
│   │   │   ├── __init__.py
│   │   │   ├── defaults.py   ← 默认规范常量
│   │   │   ├── custom.py     ← 自定义设置合并
│   │   │   └── fonts.py      ← 东亚字体处理 + Times New Roman
│   │   │
│   │   ├── preview/          ← 板块5：预览服务
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← /api/preview/{job_id}
│   │   │   └── service.py    ← 结构化内容提取
│   │   │
│   │   ├── job_manager/      ← 板块6：任务管理
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← /api/format/select-mode, /api/format/job/{id}
│   │   │   ├── service.py    ← Job生命周期状态机
│   │   │   └── models.py     ← FormatJob ORM模型
│   │   │
│   │   └── template_manager/ ← 板块7：模板管理
│   │       ├── __init__.py
│   │       ├── router.py     ← /api/templates/*
│   │       ├── service.py    ← 模板CRUD
│   │       └── models.py     ← FormatTemplate ORM模型
│   │
│   └── shared/               ← 板块间共享
│       ├── schemas.py        ← 所有Pydantic请求/响应模型
│       └── errors.py         ← 统一错误类型
│
├── uploads/                   ← 用户上传文件
├── outputs/                   ← 排版输出文件
├── requirements.txt
└── .env
```

---

## 四、前端目录结构

```
frontend/src/
├── App.tsx                   ← 框架入口：BrowserRouter + 路由
├── main.tsx                  ← React入口
├── index.css                 ← 全局样式
├── pages/
│   ├── HomePage.tsx          ← 首页
│   ├── ProcessPage.tsx       ← 处理流程（状态机驱动）
│   └── NotFoundPage.tsx      ← 404
├── modules/
│   ├── upload/               ← 对应板块1
│   │   ├── FileUploader.tsx
│   │   ├── UploadProgress.tsx
│   │   └── useFileUpload.ts  ← 真实XMLHttpRequest进度
│   ├── analyze/              ← 对应板块2
│   │   ├── ModeSelector.tsx
│   │   ├── StructureTree.tsx
│   │   ├── AnnotationPanel.tsx
│   │   └── useAnalysis.ts
│   ├── format/               ← 对应板块3+4
│   │   ├── FormatSettingsPanel.tsx
│   │   └── useFormatSettings.ts
│   ├── result/               ← 对应板块5
│   │   ├── ResultPreview.tsx
│   │   ├── CommandInput.tsx
│   │   ├── FormatTooltip.tsx
│   │   └── DownloadButton.tsx
│   ├── template/             ← 对应板块7
│   │   ├── TemplateManager.tsx
│   │   └── useTemplate.ts
│   └── history/              ← 前端独有
│       ├── HistoryPanel.tsx
│       └── useHistory.ts
├── components/
│   ├── layout/               ← Header, Footer, Layout
│   ├── common/               ← LoadingSpinner, ErrorAlert, WarningBanner, StepNavigation
│   └── ui/                   ← shadcn/ui基础组件
├── services/api.ts           ← 统一API客户端（fetch封装）
├── types/index.ts            ← 全局TypeScript类型
└── lib/utils.ts              ← cn()工具函数
```

---

## 五、各板块详细设计

### 板块9：基础设施

**公开接口**：无（被所有板块依赖）

**文件**：
- `config.py`：`Settings` 类（deepseek_api_key, deepseek_base_url, database_url, upload_dir, output_dir）。启动时校验 api_key 非空，空则打印警告。
- `database.py`：`engine`, `SessionLocal`, `Base`, `get_db()` 依赖注入。
- `main.py`：`create_app()` 工厂函数。CORS allow localhost:5173。`init_app()`：创建目录、`Base.metadata.create_all()`、注册所有板块router、调用 `TemplateService.seed_default()`。

**修复**：
- 目录创建从模块级 import 移入 `init_app()`。
- `datetime.utcnow` → `datetime.now(datetime.UTC)`。
- CORS hosts 从环境变量读取（开发默认 localhost:5173）。

---

### 板块4：格式标准

**公开接口**：
```python
# defaults.py
get_page_spec() -> dict            # 页边距: 四边2.5cm
get_heading_spec(level: int) -> dict
get_special_heading_spec() -> dict  # 摘要/目录/致谢/参考文献: 黑体小三号15pt加粗
get_body_spec() -> dict
get_caption_spec() -> dict          # 图题/表题: 宋体小五9pt
get_reference_spec() -> dict        # 宋体五号10.5pt
get_header_footer_spec() -> dict
get_title_spec() -> dict            # 论文标题: 黑体二号22pt居中加粗
get_subtitle_spec() -> dict         # 副标题: 宋体小三15pt居中

# custom.py
merge_settings(custom: dict | None, enabled: dict | None) -> dict

# fonts.py
set_east_asian_font(run, font_name: str) -> None
set_latin_font(run, font_name: str) -> None  # 新增：Times New Roman
```

**默认格式规范（完整版）**：

| 元素 | 字体 | 字号 | 加粗 | 对齐 | 行距 | 其他 |
|------|------|------|------|------|------|------|
| 论文标题 | 黑体 | 二号(22pt) | 是 | 居中 | 固定20磅 | 无下划线 |
| 副标题 | 宋体 | 小三(15pt) | 否 | 居中 | — | — |
| 特殊标题(摘要/关键词/目录/致谢/参考文献) | 黑体 | 小三(15pt) | 是 | — | 固定20磅 | — |
| 一级标题(一、) | 黑体 | 四号(14pt) | 是 | — | 固定20磅 | 独占一行 |
| 二级标题((一)) | 宋体 | 小四(12pt) | 是 | — | 固定20磅 | — |
| 三级标题(1.) | 宋体 | 小四(12pt) | 否 | — | 固定20磅 | — |
| 四级标题((1)) | 宋体 | 小四(12pt) | 否 | — | 固定20磅 | — |
| 正文 | 宋体 | 小四(12pt) | 否 | 两端对齐 | 1.5倍 | 首行缩进2字符，段前0段后0 |
| 英文/数字/公式 | Times New Roman | 同所在段 | 同所在段 | 同所在段 | — | 正文中混排 |
| 题注(图/表) | 宋体 | 小五(9pt) | 否 | 居中 | — | 图下表中 |
| 参考文献 | 宋体 | 五号(10.5pt) | 否 | 左对齐 | 单倍 | — |
| 脚注/尾注 | 宋体 | 五号(10.5pt) | 否 | — | — | — |
| 页眉 | 宋体(论文题目) | 小五(9pt) | 否 | 居中 | — | — |
| 页码 | — | — | — | 底部居中 | — | 阿拉伯数字 |
| 页面 | A4 | — | — | 纵向无分栏 | — | 四边2.5cm |

**中文字号→pt映射**（内部使用）：
- 二号 = 22pt
- 小三 = 15pt
- 四号 = 14pt
- 小四 = 12pt
- 五号 = 10.5pt
- 小五 = 9pt

---

### 板块1：文件处理

**依赖**：板块9

**公开接口**：
```python
class FileService:
    @staticmethod
    def validate(filename: str, file_size: int) -> str | None
    @staticmethod
    def save(file_bytes: bytes, original_name: str) -> tuple[str, str]
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str
    @staticmethod
    def get_output_path(job_id: str) -> Path | None
```

**API路由**：
```
POST /api/upload          → multipart上传，返回JobResponse(201)
GET  /api/download/{id}   → 返回application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

**extract_text 实现**：
- DOCX: python-docx逐段读取 `para.text`，非空段落拼接
- PDF: PyPDF2逐页 `page.extract_text()`
- 截断到20000字符（尽量在段落边界截断）

---

### 板块6：任务管理

**依赖**：板块9

**状态机**：
```
UPLOADED → ANALYZING → ANALYZED → FORMATTING → COMPLETED
              ↓            ↓           ↓
            FAILED       FAILED      FAILED
```

**FormatJob 数据模型**：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) PK | UUID |
| original_filename | String(255) | 原始文件名 |
| file_path | String(500) | 上传路径 |
| file_type | String(4) | "pdf"/"docx" |
| format_mode | String(10) | "auto"/"manual" |
| status | String(20) | JobStatus枚举值 |
| ai_analysis | String(50000) | **JSON字符串**（修复：不再用str(dict)） |
| user_annotations | String(50000) | 手动标注JSON |
| output_path | String(500) | 输出文件路径 |
| price | Float | 默认9.9 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**公开接口**：
```python
class JobService:
    @staticmethod
    def create(filename, file_path, file_type, db) -> FormatJob
    @staticmethod
    def get(job_id, db) -> FormatJob | None
    @staticmethod
    def set_status(job_id, status, db) -> FormatJob
    @staticmethod
    def save_analysis(job_id, analysis_dict, db) -> FormatJob  # json.dumps(analysis_dict)
    @staticmethod
    def save_annotations(job_id, annotations_json, db) -> FormatJob
    @staticmethod
    def save_output(job_id, output_path, db) -> FormatJob
    @staticmethod
    def to_response(job) -> JobResponse
```

**API路由**：
```
POST /api/format/select-mode      → {job_id, format_mode}
GET  /api/format/job/{id}         → JobResponse
```

---

### 板块2：AI分析引擎

**依赖**：板块1（extract_text）、板块9（settings）

**公开接口**：
```python
class AIService:
    @staticmethod
    def analyze(file_path: str, file_type: str) -> dict
    @staticmethod
    def detect_warnings(structure: dict) -> dict
```

**AI调用流程**：
1. `FileService.extract_text()` 获取论文前20000字符
2. 构造请求：`messages=[{role:"system", content:SYSTEM_PROMPT}, {role:"user", content:text}]`
3. 调用 DeepSeek API：`response_format={"type": "json_object"}`, `temperature=0.1`
4. 解析 JSON，失败则修复截断（统计 `{`/`[` 和 `}`/`]` 数量，补齐缺失）
5. 返回 structure dict

**AI输出格式（SYSTEM_PROMPT要求）**：
```json
{
  "title": "论文标题",
  "subtitle": "副标题（可选，null表示无）",
  "sections": [
    {
      "level": 1,
      "numbering": "一、",
      "title": "绪论",
      "start_marker": "绪论",
      "content_summary": "本节介绍研究背景...",
      "has_figures": false,
      "has_tables": false
    }
  ],
  "has_abstract": true,
  "has_abstract_en": true,
  "has_toc": true,
  "has_references": true,
  "has_appendix": false,
  "has_acknowledgement": true
}
```

**SYSTEM_PROMPT 关键规则**：
- 识别中文序号模式：`一、二、三、` / `（一）（二）` / `1. 2. 3.` / `(1) (2) (3)`
- 识别特殊节名：摘要、Abstract、目录、参考文献、致谢、附录 → level=0（特殊类型）
- `start_marker` = **该节标题文字本身的前20字**（不是正文前20字！）
- 论文标题和副标题分别返回

**格式警告检测**：
- `missing_abstract`：has_abstract=false
- `missing_toc`：has_toc=false
- `missing_references`：has_references=false
- `missing_figure_labels`：sections中含图但无图序文字
- `missing_table_labels`：sections中含表但无表序文字
- `conflicting_headings`：同级标题编号跳跃

**API路由**：
```
POST /api/format/analyze?job_id={id}    → 异步执行分析，更新Job状态
```

**修复**：
- HTTP client 模块级复用
- `_has_figure_label` / `_has_table_label` 改用正则 `图\d+` / `表\d+`

---

### 板块3：排版引擎

**依赖**：板块4（格式标准）、板块1（文本提取）

**公开接口**：
```python
class FormatEngine:
    @staticmethod
    def execute(
        input_path: str,
        output_path: str,
        structure: dict,
        custom_settings: dict | None = None,
        enabled_flags: dict | None = None,
    ) -> None

    @staticmethod
    def preview_formatted(
        input_path: str,
        structure: dict,
    ) -> list[dict]
```

**排版执行流程**：
1. 打开 docx：`Document(input_path)`
2. 检测并移除旧目录（查找"目录"关键词 → 移除到正文第一个标题前）
3. 应用页面设置（`apply_page_spec` → 四边2.5cm）
4. 段落匹配循环：遍历所有段落
   - **跳过表格内段落**（父元素含 `w:tc`）
   - **跳过图片段落**（含 `wp:inline` / `wp:anchor`）
   - 匹配段落文本到章节标题 → 应用对应格式
   - 未匹配 → 检查是否题注 → 题注格式 / 正文格式
5. 处理页眉页脚
6. 生成目录（正文第一个标题前插入）
7. 保存到 `output_path`

**段落匹配逻辑（matcher.py，核心）**：
```python
def match_paragraph(text: str, structure: dict, matched_sections: set) -> tuple[str, int | None]:
    """
    返回: (匹配类型, 标题级别)
    匹配类型: "paper_title" | "subtitle" | "special_heading" | "heading" | "body"
    """
    # Strategy 0: 论文标题
    if structure.title and is_title_match(text, structure.title):
        matched_sections.add("__title__")
        return ("paper_title", 0)
    
    # Strategy 0b: 副标题
    if structure.get("subtitle") and is_title_match(text, structure.subtitle):
        matched_sections.add("__subtitle__")
        return ("subtitle", 0)
    
    # Strategy 0c: 特殊标题（摘要/目录/致谢/参考文献/Abstract）
    special_keywords = ["摘要", "Abstract", "目录", "参考文献", "致谢", "附录"]
    for kw in special_keywords:
        if kw in text and kw not in matched_sections:
            matched_sections.add(kw)
            return ("special_heading", 0)
    
    # Strategy 1: 章节标题文字精确匹配
    for section in structure.sections:
        title = section.get("title", "")
        numbering = section.get("numbering", "")
        full_title = f"{numbering}{title}" if numbering else title
        if full_title not in matched_sections and is_title_match(text, full_title):
            matched_sections.add(full_title)
            return ("heading", section.get("level", 1))
    
    # Strategy 2: start_marker 兜底（仅未匹配的section）
    for section in structure.sections:
        title = section.get("title", "")
        numbering = section.get("numbering", "")
        full_title = f"{numbering}{title}" if numbering else title
        if full_title in matched_sections:
            continue
        marker = section.get("start_marker", "")
        if marker and len(marker) >= 6 and marker in text:
            # 确认 marker 不含正文常见开头词（"本文"、"研究"等）
            if not _is_body_signal(marker):
                matched_sections.add(full_title)
                return ("heading", section.get("level", 1))
    
    return ("body", None)

def is_title_match(para_text: str, title: str) -> bool:
    """检查段落文本是否匹配标题"""
    clean_para = para_text.strip().replace(" ", "")
    clean_title = title.strip().replace(" ", "")
    if not clean_para or not clean_title:
        return False
    # 精确匹配
    if clean_para == clean_title:
        return True
    # 段落以标题开头（不超过20字符偏差）
    if clean_para.startswith(clean_title) and len(clean_para) - len(clean_title) <= 20:
        return True
    # 短段落(≤30字)且标题是段落的子串
    if len(clean_para) <= 30 and clean_title in clean_para:
        return True
    return False
```

**格式应用（applier.py）**：

根据匹配结果应用格式：
- `paper_title` → `get_title_spec()` (黑体二号22pt居中加粗)
- `subtitle` → `get_subtitle_spec()` (宋体小三15pt居中)
- `special_heading` → `get_special_heading_spec()` (黑体小三15pt加粗)
- `heading` + level → `get_heading_spec(level)` (黑体/宋体 + 对应字号 + 加粗/常规)
- `body` + 以"图"/"表"开头 → `get_caption_spec()` (宋体小五9pt)
- `body` + 在参考文献区 → `get_reference_spec()` (宋体五号10.5pt)
- `body` → `get_body_spec()` (宋体小四12pt, 1.5倍行距, 首行缩进2字符)

如果有 custom_settings + enabled_flags，先调 `merge_settings()` 合并后再应用。

**英文/数字字体**：正文段落中的英文字母和数字的 run 额外设置 `font.name = "Times New Roman"`。

**PDF 输入处理**：
- PDF 排版后输出为 DOCX 格式
- 输出文件名**强制改为 .docx 扩展名**（修复旧Bug）

**API路由**：
```
POST /api/format/annotate                 → 保存手动标注JSON
POST /api/format/customize                → 保存自定义格式设置JSON
POST /api/format/execute?job_id={id}      → 执行排版
POST /api/format/modify-section/{id}       → 修改单个章节正文
```

---

### 板块5：预览服务

**依赖**：板块3（复用 matcher.py）

**公开接口**：
```python
class PreviewService:
    @staticmethod
    def extract(file_path: str, structure: dict) -> list[dict]
```

**提取逻辑**：
1. 打开 docx，遍历所有正文段落（跳过表内段、图片段）
2. 复用 `matcher.match_paragraph()` 确定每段归属哪个章节
3. 检测图片/表格：含 `wp:inline`/`wp:anchor` → 插入 ContentMarker；父标签 `w:tc` → 表格占位
4. 检测目录区：连续段落含"目录"关键词 → 标记 `is_toc=True`
5. 按章节聚合成 `[{level, title, content[], markers[]}, ...]`

**API路由**：
```
GET /api/preview/{job_id}     → PreviewResponse
```

**修复**：
- `ai_analysis` 解析用 `json.loads`（后端已改JSON存储）
- 图片检测扩展命名空间：`a:blip`

---

### 板块7：模板管理

**依赖**：板块9

**FormatTemplate 数据模型**：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增 |
| name | String(100) unique | 模板名 |
| settings_json | String(50000) | FormatSettings JSON |
| created_at | DateTime | 创建时间 |

**公开接口**：
```python
class TemplateService:
    @staticmethod
    def create_or_update(name, settings_json, db) -> FormatTemplate  # upsert
    @staticmethod
    def list_all(db) -> list[FormatTemplate]
    @staticmethod
    def get(template_id, db) -> FormatTemplate | None
    @staticmethod
    def delete(template_id, db) -> bool  # "系统默认"禁止删除
    @staticmethod
    def seed_default(db) -> None  # init_app 时调用
```

**API路由**：
```
POST   /api/templates/save
GET    /api/templates/
GET    /api/templates/{id}
DELETE /api/templates/{id}
```

---

### 板块8：前端UI

**依赖**：后端所有板块的API

**页面树**：
```
App
├── HomePage — 上传入口 + 历史记录
└── ProcessPage — 处理流程（useFormatting状态机驱动）
    ├── ModeSelector — 自动/手动
    ├── AnnotationPanel + StructureTree — 手动标注
    ├── WarningBanner — 格式警告
    ├── FormatSettingsPanel — 自定义格式
    ├── TemplateManager — 模板
    └── ResultPreview + CommandInput + FormatTooltip — 预览/修改/下载
```

**useFormatting 状态机**：
```
idle → selecting → analyzing → analyzed → formatting → done
                          ↓           ↓           ↓
                        error       error       error
```

**状态变迁**：
| 状态 | 显示内容 | 下一步触发 |
|------|---------|-----------|
| idle | 获取Job信息中 | 自动跳转 |
| selecting | ModeSelector | 用户选择 → selectMode() |
| analyzing | LoadingSpinner("AI分析中...") | API返回 → 自动 |
| analyzed(自动) | 分析结果摘要 | 自动 → executeFormatting() |
| analyzed(手动) | AnnotationPanel | 用户确认 → submitAnnotations() |
| formatting | LoadingSpinner("排版中...") | API返回 → 自动 |
| done | ResultPreview + 下载 | 用户浏览/下载 |
| error | ErrorAlert + 重试 | 用户重试 |

**关键Bug修复**：
- `ai_analysis` 前端解析：用 `JSON.parse`（后端已统一JSON格式）
- 上传进度：改为 `XMLHttpRequest` 真实进度（不再模拟）
- `useTemplate.saveTemplate`：先查同名→有则替换、无则新增
- `FormatTooltip`：增加 scroll 事件监听
- `CommandInput`：unmount 时 `clearTimeout`
- `DownloadButton` 组件：删除未使用的独立组件（ResultPreview已内联下载链接）

**依赖清理**：
- 删除 `class-variance-authority`（未使用）
- 删除 `aiofiles`（未使用）

---

## 六、构建顺序（自底向上）

```
第1步: 板块9 基础设施     → 配置、数据库、main.py框架
第2步: 板块4 格式标准      → 默认规范常量（更新为护理学论文规范）、字体处理、自定义合并
第3步: 板块1 文件处理      → 上传/下载/文本提取
第4步: 板块6 任务管理      → Job模型、状态机、CRUD
第5步: 板块2 AI分析        → DeepSeek调用、SYSTEM_PROMPT（更新编号体系）、警告检测
第6步: 板块3 排版引擎      → 匹配器、格式应用、目录生成、PDF处理
第7步: 板块5 预览服务      → 结构化内容提取
第8步: 板块7 模板管理      → 模板CRUD
第9步: 板块8 前端UI        → 页面、组件、hooks修复
```

每步验证标准：
1. 该板块的公开接口可正常调用
2. 不依赖未完成的板块
3. 上一个板块的验证不退化

---

## 七、核心Bug修复清单

| # | Bug | 根因 | 修复方案 | 板块 |
|---|-----|------|---------|------|
| 1 | 粗体传播到正文 | AI的start_marker是正文文字，匹配逻辑误把正文当标题 | 标题文字优先匹配 + start_marker兜底 + matched_sections防重复 | 板块3 |
| 2 | 字体变蓝 | 未复现，待观察 | 排版后加验证：遍历所有run检查颜色，发现非黑色则重置 | 板块3 |
| 3 | 表格图片占位丢失 | 命名空间不全 + 表内段未跳过 | 扩展NS（wp:inline/anchor, a:blip）+ matcher跳过w:tc | 板块3+5 |
| 4 | 摘要格式丢失 | 匹配不到摘要段 | 新增special_heading类型，关键词列表含"摘要" | 板块3 |
| 5 | 参考文献标题化 | "参考文献"被当成普通一级标题 | special_heading类型处理 | 板块3 |
| 6 | ai_analysis前端不显示 | 后端存str(dict)，前端JSON.parse失败，catch{}静默吞错 | 后端统一json.dumps存储 | 板块6 |
| 7 | PDF输出扩展名错误 | 输出docx但保留.pdf后缀 | 强制改扩展名 | 板块3 |
| 8 | 上传进度模拟 | useFileUpload用setInterval假进度 | 改用XMLHttpRequest onprogress | 板块8 |

---

## 八、不做的事情（范围边界）

- 支付功能（XPay集成）
- 用户登录/权限系统
- 真实页码计算（目录放"[页码]"占位符）
- PDF完美排版（只做文本提取 + 基本格式）
- 生产环境部署配置（CORS hosts留localhost）
- 邮件/短信通知
- 并行处理/队列

---

## 九、启动方式

```bash
# 后端
cd C:\Users\博博\paper-formatter\backend
python -m uvicorn app.main:app --port 8000 --reload

# 前端
cd C:\Users\博博\paper-formatter\frontend
npx vite --port 5173
```

启动前检查：
- [ ] `.env` 中 `DEEPSEEK_API_KEY` 有效
- [ ] 后端端口 8000 未被占用
- [ ] `vite.config.ts` proxy target 为 `http://127.0.0.1:8000`
- [ ] Python 依赖已安装（`pip install -r requirements.txt`）
- [ ] npm 依赖已安装（`npm install`）

---

## 十、测试方案

**标准文件**：`D:\HuaweiMoveData\Users\博博\Desktop\新型冠状病毒感染后呼吸系统康复护理的循证实践研究.docx`（格式正确）

**测试输入**：基于标准文件制作格式打乱版本

**验证方法**：每完成一个核心板块（3排版引擎），上传打乱文件 → 排版 → 下载 → 人工逐项对照：
1. 页面边距四边2.5cm
2. 标题层级字体字号加粗正确
3. 正文宋体小四1.5倍行距首行缩进
4. 题注居中宋体小五
5. 参考文献宋体五号
6. 英文数字Times New Roman
