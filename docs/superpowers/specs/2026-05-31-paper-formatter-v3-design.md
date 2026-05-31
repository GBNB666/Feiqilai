# Paper-Formatter V3 设计文档

## 项目目标

上传 docx 论文 → AI 分析结构 → 按护理学论文学术规范自动排版 → 浏览器下载。

**成功标准：** 在浏览器里完整走通：上传 docx → AI 分析 → 排版 → 下载，格式正确，无控制台报错。

**失败/不该做：** 模板管理、格式设置面板、手动标注、章节修改、目录生成、页眉页脚、历史记录、定价支付、PDF 支持。

---

## 一、V2→V3 变化

| V2 | V3 | 原因 |
|----|-----|------|
| 9 板块 | 5 板块 | 砍掉预览独立服务、模板管理、任务管理 ORM、前端多页面 |
| SQLAlchemy ORM + FormatJob 模型 | 内存字典 job_store | 单用户场景，ORM 是过度工程 |
| 18 个 API 端点 | 5 个 API 端点 | 只留核心链路 |
| 多页面（HomePage + ProcessPage） | 单页面状态机 | 少路由少 bug |
| 先建全部后端再前端 | 写一个 API → 接前端 → 浏览器验证 → 下一个 | 当场发现 bug |
| format_engine 有 customize/annotate/modify-section 路由 | 只保留 execute | 不做手动标注和自定义 |

---

## 二、技术栈

| 层 | 技术 |
|----|------|
| 后端框架 | Python + FastAPI |
| 数据库 | 内存字典（无 SQLite/SQLAlchemy 依赖） |
| 文档处理 | python-docx |
| AI | DeepSeek API (response_format=json_object) |
| 前端 | React 19 + TypeScript + Vite + Tailwind CSS 4 + shadcn/ui |

---

## 三、后端架构

### 目录结构

```
backend/
├── app/
│   ├── main.py              ← FastAPI 入口，CORS，注册路由
│   ├── config.py             ← Settings (pydantic-settings)
│   │
│   ├── modules/
│   │   ├── format_standards/ ← 板块1：格式标准
│   │   │   ├── __init__.py
│   │   │   ├── defaults.py   ← 格式常量（页面/标题4级/特殊标题/正文/参考文献）
│   │   │   └── fonts.py      ← 东亚字体 + Times New Roman
│   │   │
│   │   ├── file_handler/     ← 板块2：文件处理
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← POST /api/upload, GET /api/download/{id}
│   │   │   ├── service.py    ← 验证、保存、提取文本、获取输出路径
│   │   │   └── extractors.py ← DOCX 文本提取
│   │   │
│   │   ├── ai_analyzer/      ← 板块3：AI 分析
│   │   │   ├── __init__.py
│   │   │   ├── router.py     ← POST /api/analyze/{id}
│   │   │   ├── service.py    ← DeepSeek 调用、JSON 解析
│   │   │   ├── prompt.py     ← SYSTEM_PROMPT
│   │   │   └── warnings.py   ← 格式警告检测
│   │   │
│   │   └── format_engine/    ← 板块4：排版引擎
│   │       ├── __init__.py
│   │       ├── router.py     ← POST /api/format/{id}
│   │       ├── service.py    ← 排版编排
│   │       ├── matcher.py    ← 段落→章节匹配（三策略）
│   │       └── applier.py    ← 格式应用
│   │
│   ├── shared/
│   │   ├── schemas.py        ← Pydantic 请求/响应模型
│   │   └── errors.py         ← AppError（继承 HTTPException）
│   │
│   └── job_store.py          ← 内存字典，Job CRUD
│
├── uploads/
├── outputs/
├── requirements.txt
└── .env
```

### API 端点（5 个）

```
POST /api/upload              → multipart 上传，返回 {id, filename, status}
GET  /api/download/{id}       → 返回 docx 文件流 (Content-Disposition: attachment)
POST /api/analyze/{id}        → AI 分析，返回 {id, status, structure, warnings}
POST /api/format/{id}         → 执行排版，返回 {id, status, download_url}
GET  /api/health              → {"status": "ok"}
```

### job_store.py 接口

```python
# 内存字典，key=job_id(str), value=dict
jobs: dict[str, dict] = {}

def create_job(filename: str, file_path: str, file_type: str) -> dict
def get_job(job_id: str) -> dict | None
def update_job(job_id: str, **kwargs) -> dict
```

每个 job dict 结构：
```python
{
    "id": "uuid",
    "original_filename": "论文.docx",
    "file_path": "uploads/uuid.docx",
    "file_type": "docx",
    "status": "uploaded",  # uploaded → analyzing → analyzed → formatting → done
    "structure": None,      # AI 分析结果 dict
    "warnings": None,       # 格式警告
    "output_path": None,    # 排版输出路径
}
```

### 关键修复（直接来自 V2 复盘）

1. **AppError 继承 HTTPException** — 不搞自定义 handler
2. **所有接口返回字段统一用 `id`** — 不用 `job_id`
3. **下载用 `Content-Disposition: attachment`** — 前端 `<a target="_blank">` 不设 download 属性
4. **AI 分析结果用 json.dumps 存储** — 前端 JSON.parse 解析
5. **matcher Strategy 0c 用 `startswith` + 长度 ≤ 30** — 不做子串匹配
6. **matcher 加 `_is_toc_entry()` 检测** — 防止目录条目污染章节匹配

---

## 四、前端架构

### 目录结构

```
frontend/src/
├── App.tsx                ← 单页面状态机（idle→uploading→analyzing→formatting→done）
├── main.tsx               ← React 入口
├── index.css              ← Tailwind + 全局样式
├── types/index.ts         ← TypeScript 类型（与后端 schemas.py 字段逐字对齐）
├── services/api.ts        ← fetch 封装
└── components/
    ├── FileUploader.tsx    ← 拖拽上传 + XMLHttpRequest 真实进度
    ├── AnalyzePanel.tsx    ← 分析中 loading + 结构展示
    ├── ResultView.tsx      ← 下载按钮（a target=_blank）
    └── StepIndicator.tsx   ← 四步进度指示
```

### 状态机

```
idle → uploading → analyzing → formatting → done
  ↓        ↓           ↓            ↓
  └────────┴───────────┴────────────┘
                 error
```

### 字段对齐规则

前后端类型文件必须逐字段一致。示例：

```typescript
// frontend/src/types/index.ts
interface JobResponse {
  id: string;           // ← 后端也是 "id"
  original_filename: string;
  status: string;
  structure?: Section[];
  warnings?: Warning[];
  download_url?: string;
}

interface Section {
  level: number;
  numbering: string;
  title: string;
  start_marker: string;
  content_summary: string;
}
```

```python
# backend/app/shared/schemas.py
class JobResponse(BaseModel):
    id: str              # ← 前端也是 "id"
    original_filename: str
    status: str
    structure: list[Section] | None = None
    warnings: list[Warning] | None = None
    download_url: str | None = None
```

---

## 五、格式规范（护理学论文标准）

与 V2 设计文档第 4 节完全一致，不复述。关键点：
- 四级标题：一、(一)、1.、(1)
- 特殊标题：摘要/Abstract/关键词/目录/参考文献/致谢/附录
- 黑体用于论文标题 + 一级标题 + 特殊标题
- 宋体用于正文 + 二级及以下标题
- Times New Roman 用于英文和数字
- 正文小四 12pt / 1.5 倍行距 / 首行缩进 2 字符 / 两端对齐

---

## 六、构建顺序（每步浏览器验证）

### 第 0 步：项目脚手架
- 创建 backend/ 和 frontend/ 目录结构
- backend requirements.txt + frontend package.json
- 验证：uvicorn 启动成功，vite 启动成功

### 第 1 步：格式标准
- defaults.py + fonts.py
- 验证：导入无报错

### 第 2 步：文件处理（上传 + 下载）
- file_handler 模块（router + service + extractors）
- 前端 FileUploader 组件
- **浏览器验证**：上传 docx，确认返回 JSON 含 filename 和 id；下载端点返回文件

### 第 3 步：AI 分析
- ai_analyzer 模块（router + service + prompt + warnings）
- 前端 AnalyzePanel 组件
- **浏览器验证**：上传后点分析，确认返回正确的章节结构 JSON

### 第 4 步：排版引擎
- format_engine 模块（router + service + matcher + applier）
- 前端 ResultView 组件
- **浏览器验证**：上传→分析→排版→下载，打开文件确认格式正确

### 第 5 步：前端打磨
- StepIndicator + 错误提示 + loading 状态
- **浏览器验证**：全流程无控制台报错，UI 流畅

---

## 七、不做

模板管理/保存/切换、格式设置面板、手动标注模式、章节修改/重新排版、目录生成、页眉页脚、历史记录、定价/支付、PDF 支持

---

## 八、启动方式

```bash
# 后端
cd backend && python -m uvicorn app.main:app --port 8000 --reload

# 前端
cd frontend && npx vite --port 5173
```

## 九、测试文件

标准论文：`D:\HuaweiMoveData\Users\博博\Desktop\新型冠状病毒感染后呼吸系统康复护理的循证实践研究.docx`
