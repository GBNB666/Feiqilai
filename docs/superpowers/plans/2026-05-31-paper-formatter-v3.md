# Paper-Formatter V3 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 构建论文AI格式排版网站——上传docx → AI分析 → 排版 → 下载，护理学论文标准，每步浏览器验证

**架构：** 精简V2架构为5个核心板块（格式标准→文件处理→AI分析→排版引擎）+ 单页面React前端，内存字典管理Job，5个API端点

**技术栈：** Python FastAPI + python-docx + DeepSeek API + React 19 + TypeScript + Vite + Tailwind CSS 4

---

## 文件树总览

```
paper-formatter/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── job_store.py              ← 内存字典，Job CRUD
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── errors.py             ← AppError(HTTPException)
│   │   │   └── schemas.py            ← Pydantic models
│   │   └── modules/
│   │       ├── format_standards/
│   │       │   ├── __init__.py
│   │       │   ├── defaults.py
│   │       │   └── fonts.py
│   │       ├── file_handler/
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── service.py
│   │       │   └── extractors.py
│   │       ├── ai_analyzer/
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── service.py
│   │       │   ├── prompt.py
│   │       │   └── warnings.py
│   │       └── format_engine/
│   │           ├── __init__.py
│   │           ├── router.py
│   │           ├── service.py
│   │           ├── matcher.py
│   │           └── applier.py
│   ├── uploads/                      ← 自动创建
│   ├── outputs/                      ← 自动创建
│   ├── requirements.txt
│   └── .env                          ← 从 .env.backup 复制
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── components/
│   │       ├── FileUploader.tsx
│   │       ├── AnalyzePanel.tsx
│   │       ├── ResultView.tsx
│   │       └── StepIndicator.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   └── package.json
│
├── .env.backup
├── docs/
└── START-HERE.md
```

---

### 任务 0：项目脚手架

**文件：**
- 创建：`backend/requirements.txt`
- 创建：`backend/.env`
- 创建：`backend/app/__init__.py`
- 创建：`backend/app/config.py`
- 创建：`backend/app/main.py`
- 创建：`backend/app/job_store.py`
- 创建：`backend/app/shared/__init__.py`
- 创建：`backend/app/shared/errors.py`
- 创建：`backend/app/shared/schemas.py`
- 创建：`frontend/` (Vite + React + TypeScript + Tailwind)
- 创建：`frontend/src/types/index.ts`

- [ ] **步骤 0.1：创建后端 requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-docx==1.1.2
python-multipart==0.0.12
pydantic-settings==2.5.2
httpx==0.27.2
```

- [ ] **步骤 0.2：复制 .env 文件**

```bash
cp .env.backup backend/.env
```

- [ ] **步骤 0.3：创建 backend/app/config.py**

```python
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

if not settings.deepseek_api_key:
    print("WARNING: DEEPSEEK_API_KEY is empty! AI analysis will fail.")

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)
```

- [ ] **步骤 0.4：创建 backend/app/shared/errors.py**

```python
from fastapi import HTTPException


class AppError(HTTPException):
    """Base application error. Inherits from HTTPException so FastAPI handles it natively."""
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, message=message)


class FileValidationError(AppError):
    def __init__(self, message: str = "Invalid file"):
        super().__init__(status_code=400, message=message)


class AIError(AppError):
    def __init__(self, message: str = "AI analysis failed"):
        super().__init__(status_code=500, message=message)


class FormatError(AppError):
    def __init__(self, message: str = "Formatting failed"):
        super().__init__(status_code=500, message=message)
```

- [ ] **步骤 0.5：创建 backend/app/shared/schemas.py**

```python
from pydantic import BaseModel


class Section(BaseModel):
    level: int
    numbering: str
    title: str
    start_marker: str
    content_summary: str


class Warning(BaseModel):
    type: str
    message: str


class JobResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    status: str
    structure: list[Section] | None = None
    warnings: list[Warning] | None = None
    download_url: str | None = None


class AnalyzeRequest(BaseModel):
    job_id: str


class FormatRequest(BaseModel):
    job_id: str
```

- [ ] **步骤 0.6：创建 backend/app/job_store.py**

```python
"""In-memory job storage. Single-user app, no ORM needed."""
import uuid
from datetime import datetime, timezone


jobs: dict[str, dict] = {}


def create_job(filename: str, file_path: str, file_type: str) -> dict:
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "original_filename": filename,
        "file_path": file_path,
        "file_type": file_type,
        "status": "uploaded",
        "structure": None,
        "warnings": None,
        "output_path": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    jobs[job_id] = job
    return job


def get_job(job_id: str) -> dict | None:
    return jobs.get(job_id)


def update_job(job_id: str, **kwargs) -> dict:
    job = jobs[job_id]
    job.update(kwargs)
    return job
```

- [ ] **步骤 0.7：创建 backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="Paper Formatter V3")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **步骤 0.8：安装后端依赖并验证启动**

```bash
cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --port 8000
```

预期：访问 http://localhost:8000/api/health 返回 `{"status":"ok"}`

- [ ] **步骤 0.9：创建前端项目**

```bash
cd C:/Users/博博/paper-formatter && npm create vite@latest frontend -- --template react-ts
cd frontend && npm install && npm install tailwindcss @tailwindcss/vite
```

- [ ] **步骤 0.10：配置 frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
```

- [ ] **步骤 0.11：配置 frontend/src/index.css**

```css
@import "tailwindcss";

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
```

- [ ] **步骤 0.12：创建 frontend/src/types/index.ts**

```typescript
export interface Section {
  level: number;
  numbering: string;
  title: string;
  start_marker: string;
  content_summary: string;
}

export interface Warning {
  type: string;
  message: string;
}

export interface JobResponse {
  id: string;
  original_filename: string;
  file_type: string;
  status: string;
  structure?: Section[];
  warnings?: Warning[];
  download_url?: string;
}

export type JobStatus =
  | 'idle'
  | 'uploading'
  | 'uploaded'
  | 'analyzing'
  | 'analyzed'
  | 'formatting'
  | 'done'
  | 'error';

export type AppStep = 'upload' | 'analyze' | 'format' | 'download';
```

- [ ] **步骤 0.13：创建 frontend/src/services/api.ts**

```typescript
const BASE = '/api';

export async function apiUpload(file: File): Promise<JobResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}

export async function apiAnalyze(jobId: string): Promise<JobResponse> {
  const res = await fetch(`${BASE}/analyze/${jobId}`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}

export async function apiFormat(jobId: string): Promise<JobResponse> {
  const res = await fetch(`${BASE}/format/${jobId}`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Format failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}

export function getDownloadUrl(jobId: string): string {
  return `${BASE}/download/${jobId}`;
}
```

- [ ] **步骤 0.14：验证前端启动**

```bash
cd frontend && npx vite --port 5173
```

预期：访问 http://localhost:5173 看到 Vite + React 默认页面

- [ ] **步骤 0.15：提交**

```bash
git add -A && git commit -m "chore: project scaffold — FastAPI + Vite + React + Tailwind"
```

---

### 任务 1：格式标准

**文件：**
- 创建：`backend/app/modules/format_standards/__init__.py`
- 创建：`backend/app/modules/format_standards/defaults.py`
- 创建：`backend/app/modules/format_standards/fonts.py`

- [ ] **步骤 1.1：创建 defaults.py**

```python
"""护理学论文格式默认规范。

字号映射:
  二号=22pt, 小三=15pt, 四号=14pt, 小四=12pt, 五号=10.5pt, 小五=9pt

标题体系:
  一、(一)、1.、(1)  对应 level 1/2/3/4

特殊标题(level=0):
  摘要、Abstract、关键词、目录、参考文献、致谢、附录
"""


def get_page_spec() -> dict:
    return {
        "margin_top_cm": 2.5,
        "margin_bottom_cm": 2.5,
        "margin_left_cm": 2.5,
        "margin_right_cm": 2.5,
    }


def get_title_spec() -> dict:
    """论文标题: 黑体二号22pt居中加粗"""
    return {
        "font_name": "黑体",
        "font_size_pt": 22,
        "bold": True,
        "alignment": "center",
        "line_spacing_pt": 20,
    }


def get_subtitle_spec() -> dict:
    """副标题: 宋体小三15pt居中"""
    return {
        "font_name": "宋体",
        "font_size_pt": 15,
        "bold": False,
        "alignment": "center",
    }


def get_special_heading_spec() -> dict:
    """特殊标题(摘要/Abstract/关键词/目录/参考文献/致谢/附录): 黑体小三15pt加粗"""
    return {
        "font_name": "黑体",
        "font_size_pt": 15,
        "bold": True,
        "line_spacing_pt": 20,
    }


def get_heading_spec(level: int) -> dict:
    """根据标题级别返回格式规范。"""
    config = {
        1: {"font_name": "黑体", "font_size_pt": 14, "bold": True},
        2: {"font_name": "宋体", "font_size_pt": 12, "bold": True},
        3: {"font_name": "宋体", "font_size_pt": 12, "bold": False},
        4: {"font_name": "宋体", "font_size_pt": 12, "bold": False},
    }
    spec = config.get(level, config[4])
    spec["line_spacing_pt"] = 20
    return spec


def get_body_spec() -> dict:
    """正文: 宋体小四12pt, 1.5倍行距, 首行缩进2字符, 两端对齐"""
    return {
        "font_name": "宋体",
        "font_size_pt": 12,
        "bold": False,
        "alignment": "justify",
        "line_spacing": 1.5,
        "first_line_indent_chars": 2,
    }


def get_caption_spec() -> dict:
    """题注(图/表): 宋体小五9pt居中"""
    return {
        "font_name": "宋体",
        "font_size_pt": 9,
        "bold": False,
        "alignment": "center",
    }


def get_reference_spec() -> dict:
    """参考文献条目: 宋体五号10.5pt, 单倍行距, 左对齐"""
    return {
        "font_name": "宋体",
        "font_size_pt": 10.5,
        "bold": False,
        "alignment": "left",
        "line_spacing": 1.0,
    }
```

- [ ] **步骤 1.2：创建 fonts.py**

```python
"""East-Asian font and Latin font handling for python-docx."""
from docx.oxml.ns import qn


def set_east_asian_font(run, font_name: str) -> None:
    """Set the East-Asian font (w:eastAsia) on a run."""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:eastAsia"), font_name)


def set_latin_font(run, font_name: str) -> None:
    """Set the Latin font (w:ascii + w:hAnsi) on a run."""
    run.font.name = font_name
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)
```

- [ ] **步骤 1.3：创建 __init__.py**

```python
from app.modules.format_standards import defaults, fonts

__all__ = ["defaults", "fonts"]
```

- [ ] **步骤 1.4：验证格式标准模块**

```bash
cd backend && python -c "from app.modules.format_standards.defaults import get_body_spec; print(get_body_spec())"
```

预期：打印正文格式规范 dict

- [ ] **步骤 1.5：提交**

```bash
git add backend/app/modules/format_standards/ && git commit -m "feat: add format standards — nursing paper specs + fonts"
```

---

### 任务 2：文件处理（上传 + 下载）

这是第一个需要浏览器验证的板块。写完立即验证上传和下载。

**文件：**
- 创建：`backend/app/modules/file_handler/__init__.py`
- 创建：`backend/app/modules/file_handler/service.py`
- 创建：`backend/app/modules/file_handler/extractors.py`
- 创建：`backend/app/modules/file_handler/router.py`
- 修改：`backend/app/main.py` — 注册 file_handler router
- 创建：`frontend/src/components/FileUploader.tsx`
- 修改：`frontend/src/App.tsx` — 集成 FileUploader
- 修改：`frontend/src/App.css` — 清空默认样式

- [ ] **步骤 2.1：创建 file_handler/service.py**

```python
"""File handling: validate, save, extract text, get output path."""
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.config import settings
from app.shared.errors import FileValidationError, NotFoundError

ALLOWED_EXTENSIONS = {"docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def validate_file(filename: str, file_size: int) -> str | None:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return f"不支持的文件类型 .{ext}，仅支持 .docx"
    if file_size > MAX_FILE_SIZE:
        return f"文件过大 ({file_size / 1024 / 1024:.1f}MB)，上限 50MB"
    return None


def save_file(file: UploadFile) -> tuple[str, str, str]:
    """Save uploaded file to uploads/. Returns (file_path, file_id, original_name)."""
    file_id = str(uuid.uuid4())
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "docx"
    filename = f"{file_id}.{ext}"
    file_path = Path(settings.upload_dir).resolve() / filename

    content = file.file.read()
    file_path.write_bytes(content)

    return str(file_path), file_id, file.filename or "unknown.docx"


def get_output_path(job_id: str) -> Path | None:
    candidate = Path(settings.output_dir).resolve() / f"{job_id}.docx"
    if candidate.exists():
        return candidate
    return None
```

- [ ] **步骤 2.2：创建 file_handler/extractors.py**

```python
"""Extract text from DOCX files for AI analysis."""
from docx import Document


def extract_docx_text(file_path: str, max_chars: int = 20000) -> str:
    doc = Document(file_path)
    paragraphs = []
    total = 0
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if total + len(text) > max_chars:
            remaining = max_chars - total
            if remaining > 100:
                paragraphs.append(text[:remaining])
            break
        paragraphs.append(text)
        total += len(text)
    return "\n".join(paragraphs)
```

- [ ] **步骤 2.3：创建 file_handler/router.py**

```python
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from app.shared.errors import FileValidationError, NotFoundError
from app.job_store import create_job, get_job
from app.modules.file_handler.service import validate_file, save_file, get_output_path

router = APIRouter()


@router.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    file_size = len(content)
    await file.seek(0)

    error = validate_file(file.filename or "", file_size)
    if error:
        raise FileValidationError(message=error)

    file_path, file_id, original_name = save_file(file)
    file_type = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "docx"
    job = create_job(filename=original_name, file_path=file_path, file_type=file_type)

    return {
        "id": job["id"],
        "original_filename": job["original_filename"],
        "file_type": job["file_type"],
        "status": job["status"],
    }


@router.get("/api/download/{job_id}")
async def download(job_id: str):
    job = get_job(job_id)
    if not job:
        raise NotFoundError(message=f"任务 {job_id} 不存在")

    path = get_output_path(job_id)
    if not path:
        raise NotFoundError(message=f"排版文件不存在，请先执行排版")

    return FileResponse(
        path=str(path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=job["original_filename"].rsplit(".", 1)[0] + "_formatted.docx",
        headers={"Content-Disposition": f"attachment; filename={job['original_filename'].rsplit('.', 1)[0]}_formatted.docx"},
    )
```

- [ ] **步骤 2.4：注册 router 到 main.py**

在 `backend/app/main.py` 中，在 `app = create_app()` 之前添加：

```python
from app.modules.file_handler.router import router as file_router
app.include_router(file_router)
```

修改后 main.py 的 `create_app()` 函数末尾（return 之前）加上：
```python
    from app.modules.file_handler.router import router as file_router
    app.include_router(file_router)
```

- [ ] **步骤 2.5：用 curl 验证上传和下载端点**

启动后端后：
```bash
# 测试上传（用标准论文文件）
curl -X POST http://localhost:8000/api/upload -F "file=@D:/HuaweiMoveData/Users/博博/Desktop/新型冠状病毒感染后呼吸系统康复护理的循证实践研究.docx"

# 预期返回: {"id":"...", "original_filename":"...", "file_type":"docx", "status":"uploaded"}
```

- [ ] **步骤 2.6：创建前台上传组件 FileUploader.tsx**

```typescript
import { useState, useRef } from 'react';
import { apiUpload, type JobResponse } from '../services/api';

interface Props {
  onUploaded: (job: JobResponse) => void;
}

export default function FileUploader({ onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'docx') {
      setError('仅支持 .docx 文件');
      return;
    }
    setError('');
    setUploading(true);
    try {
      const job = await apiUpload(file);
      onUploaded(job);
    } catch (e: any) {
      setError(e.message || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="max-w-xl mx-auto mt-20">
      <h1 className="text-2xl font-bold text-center mb-2">论文格式排版</h1>
      <p className="text-center text-gray-500 mb-8">上传 docx 论文，AI 自动按护理学规范排版</p>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors
          ${dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
        {uploading ? (
          <div className="text-gray-500">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
            上传中...
          </div>
        ) : (
          <div className="text-gray-500">
            <div className="text-4xl mb-3">📄</div>
            拖拽 docx 文件到此处，或点击选择
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
```

- [ ] **步骤 2.7：更新 App.tsx**

```typescript
import { useState } from 'react';
import FileUploader from './components/FileUploader';
import { JobResponse, JobStatus } from './types';
import './App.css';

function App() {
  const [status, setStatus] = useState<JobStatus>('idle');
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState('');

  const handleUploaded = (j: JobResponse) => {
    setJob(j);
    setStatus('uploaded');
    setError('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8 px-4">
        {status === 'idle' && (
          <FileUploader onUploaded={handleUploaded} />
        )}

        {status === 'uploaded' && job && (
          <div className="max-w-xl mx-auto mt-20 text-center">
            <div className="text-green-600 text-lg mb-4">上传成功: {job.original_filename}</div>
            <div className="text-gray-400 text-sm">下一步：AI 分析（待实现）</div>
          </div>
        )}

        {error && (
          <div className="max-w-xl mx-auto mt-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
```

- [ ] **步骤 2.8：清空 App.css**

```css
/* App-specific styles — keep minimal */
```

- [ ] **步骤 2.9：浏览器验证上传**

```bash
# 启动后端 (如果还没启动)
cd backend && python -m uvicorn app.main:app --port 8000 --reload

# 启动前端 (另一个终端)
cd frontend && npx vite --port 5173
```

打开 http://localhost:5173，拖拽标准论文文件上传。
预期：显示"上传成功: xxx.docx"

- [ ] **步骤 2.10：提交**

```bash
git add -A && git commit -m "feat: add file handler — upload + download endpoints + frontend FileUploader"
```

---

### 任务 3：AI 分析

**文件：**
- 创建：`backend/app/modules/ai_analyzer/__init__.py`
- 创建：`backend/app/modules/ai_analyzer/prompt.py`
- 创建：`backend/app/modules/ai_analyzer/service.py`
- 创建：`backend/app/modules/ai_analyzer/warnings.py`
- 创建：`backend/app/modules/ai_analyzer/router.py`
- 修改：`backend/app/main.py` — 注册 ai_analyzer router
- 创建：`frontend/src/components/AnalyzePanel.tsx`
- 修改：`frontend/src/App.tsx` — 添加分析流程

- [ ] **步骤 3.1：创建 ai_analyzer/prompt.py**

```python
SYSTEM_PROMPT = """你是一位专业的学术论文格式分析专家。你的任务是将输入的论文文本分析为结构化的章节信息。

## 输出格式（严格JSON）

{
  "title": "论文主标题",
  "subtitle": "副标题（如无可设为null）",
  "sections": [
    {
      "level": 1,
      "numbering": "一、",
      "title": "绪论",
      "start_marker": "一、绪论",
      "content_summary": "本节介绍研究背景和意义"
    }
  ],
  "has_abstract": true,
  "has_abstract_en": true,
  "has_toc": true,
  "has_references": true,
  "has_appendix": false,
  "has_acknowledgement": true
}

## 标题层级

护理学论文使用四级标题体系：
- 一级标题：中文数字 + 顿号，如"一、""二、""三、"
- 二级标题：括号中文数字，如"（一）""（二）""（三）"
- 三级标题：阿拉伯数字 + 点号，如"1.""2.""3."
- 四级标题：括号阿拉伯数字，如"（1）""（2）""（3）"

## 特殊节名（level=0，这些不是普通标题）

- "摘要"、"Abstract"、"关键词"、"目录"、"参考文献"、"致谢"、"附录"
- 这些应该通过 has_* 字段标记，不放入 sections 数组

## start_marker 规则（极其重要）

start_marker 是该节标题文字本身，不是正文内容！
- 正确示例：一级标题 "一、绪论" → start_marker 应为 "一、绪论"
- 错误示例：start_marker 写成了正文的 "本文研究背景..."

## 其他规则

1. 识别正文中出现的关键词如"图1""表2"时，将对应 section 的 has_figures/has_tables 设为 true
2. 如果论文没有某个特殊节，对应的 has_* 字段设为 false
3. 仅输出 JSON，不要输出其他文字
"""
```

- [ ] **步骤 3.2：创建 ai_analyzer/service.py**

```python
import json
import httpx
from app.config import settings
from app.shared.errors import AIError

_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            base_url=settings.deepseek_base_url,
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )
    return _client


def analyze_text(text: str) -> dict:
    from app.modules.ai_analyzer.prompt import SYSTEM_PROMPT

    try:
        response = _get_client().post(
            "/chat/completions",
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "temperature": 0.1,
                "max_tokens": 4096,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return _fix_json(content)
    except httpx.HTTPError as e:
        raise AIError(message=f"AI API 调用失败: {e}")
    except (KeyError, IndexError) as e:
        raise AIError(message=f"AI 响应格式异常: {e}")


def _fix_json(raw: str) -> dict:
    """Attempt to fix truncated JSON by balancing braces."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Balance braces
    open_braces = raw.count("{") - raw.count("}")
    open_brackets = raw.count("[") - raw.count("]")
    fixed = raw
    if open_brackets > 0:
        fixed += "]" * open_brackets
    if open_braces > 0:
        fixed += "}" * open_braces

    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        raise AIError(message=f"AI 返回的 JSON 无法解析: {e}")
```

- [ ] **步骤 3.3：创建 ai_analyzer/warnings.py**

```python
import re


def detect_warnings(structure: dict, full_text: str = "") -> list[dict]:
    warnings = []

    if not structure.get("has_abstract"):
        warnings.append({"type": "missing_abstract", "message": "未检测到中文摘要"})
    if not structure.get("has_references"):
        warnings.append({"type": "missing_references", "message": "未检测到参考文献"})

    sections = structure.get("sections", [])
    for sec in sections:
        if sec.get("has_figures"):
            text = full_text or ""
            if not re.search(r"图\s*\d+", text):
                warnings.append({"type": "missing_figure_labels", "message": f"节「{sec.get('title', '')}」标注含图但未找到图序"})
        if sec.get("has_tables"):
            text = full_text or ""
            if not re.search(r"表\s*\d+", text):
                warnings.append({"type": "missing_table_labels", "message": f"节「{sec.get('title', '')}」标注含表但未找到表序"})

    return warnings
```

- [ ] **步骤 3.4：创建 ai_analyzer/router.py**

```python
from fastapi import APIRouter
from app.shared.errors import NotFoundError, AIError
from app.job_store import get_job, update_job
from app.modules.file_handler.extractors import extract_docx_text
from app.modules.ai_analyzer.service import analyze_text
from app.modules.ai_analyzer.warnings import detect_warnings
from app.shared.schemas import JobResponse

router = APIRouter()


@router.post("/api/analyze/{job_id}")
async def analyze(job_id: str):
    job = get_job(job_id)
    if not job:
        raise NotFoundError(message=f"任务 {job_id} 不存在")

    update_job(job_id, status="analyzing")

    try:
        text = extract_docx_text(job["file_path"])
        structure = analyze_text(text)
        warnings = detect_warnings(structure, text)
    except Exception:
        update_job(job_id, status="error")
        raise

    update_job(job_id, status="analyzed", structure=structure, warnings=warnings)

    return {
        "id": job_id,
        "original_filename": job["original_filename"],
        "file_type": job["file_type"],
        "status": "analyzed",
        "structure": structure.get("sections", []),
        "warnings": warnings,
    }
```

- [ ] **步骤 3.5：注册 ai_analyzer router 到 main.py**

```python
from app.modules.ai_analyzer.router import router as ai_router
app.include_router(ai_router)
```

- [ ] **步骤 3.6：curl 验证 AI 分析**

```bash
# 先上传获取 job_id
JOB_ID=$(curl -s -X POST http://localhost:8000/api/upload -F "file=@标准论文.docx" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 执行分析
curl -X POST "http://localhost:8000/api/analyze/$JOB_ID"
```

预期返回含 sections 数组的 JSON（约 30-60 秒）。

- [ ] **步骤 3.7：创建前端 AnalyzePanel.tsx**

```typescript
import { useState, useEffect } from 'react';
import { apiAnalyze } from '../services/api';
import { JobResponse, Section, Warning } from '../types';

interface Props {
  job: JobResponse;
  onAnalyzed: (job: JobResponse) => void;
  onError: (msg: string) => void;
}

export default function AnalyzePanel({ job, onAnalyzed, onError }: Props) {
  const [analyzing, setAnalyzing] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await apiAnalyze(job.id);
        if (!cancelled) {
          setAnalyzing(false);
          onAnalyzed(result);
        }
      } catch (e: any) {
        if (!cancelled) {
          setAnalyzing(false);
          onError(e.message || 'AI 分析失败');
        }
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (analyzing) {
    return (
      <div className="max-w-xl mx-auto mt-20 text-center">
        <div className="animate-spin w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-600">AI 正在分析论文结构...</p>
        <p className="text-sm text-gray-400 mt-1">这可能需要 30-60 秒</p>
      </div>
    );
  }

  return null; // 分析完成后由父组件切换状态
}

// 导出纯展示组件
export function StructureDisplay({ structure, warnings }: { structure?: Section[]; warnings?: Warning[] }) {
  return (
    <div className="max-w-xl mx-auto mt-8">
      <h2 className="text-lg font-semibold mb-4">分析结果</h2>

      {warnings && warnings.length > 0 && (
        <div className="mb-6 space-y-2">
          {warnings.map((w, i) => (
            <div key={i} className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
              {w.message}
            </div>
          ))}
        </div>
      )}

      {structure && (
        <div className="space-y-2">
          <p className="text-sm text-gray-500 mb-3">识别到 {structure.length} 个章节：</p>
          {structure.map((sec, i) => (
            <div key={i} className="flex items-center gap-3 p-2 rounded hover:bg-gray-50">
              <span className="text-xs text-gray-400 w-12 shrink-0">
                {sec.numbering || '特殊'}
              </span>
              <span className="text-sm font-medium">{sec.title}</span>
              <span className="text-xs text-gray-400 ml-auto">
                {['', '一级', '二级', '三级', '四级'][sec.level] || ''}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **步骤 3.8：更新 App.tsx 集成分析流程**

```typescript
import { useState } from 'react';
import FileUploader from './components/FileUploader';
import AnalyzePanel, { StructureDisplay } from './components/AnalyzePanel';
import { JobResponse, JobStatus } from './types';
import './App.css';

function App() {
  const [status, setStatus] = useState<JobStatus>('idle');
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState('');

  const handleUploaded = (j: JobResponse) => {
    setJob(j);
    setStatus('analyzing');
    setError('');
  };

  const handleAnalyzed = (j: JobResponse) => {
    setJob(j);
    setStatus('analyzed');
  };

  const handleError = (msg: string) => {
    setError(msg);
    setStatus('error');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8 px-4">
        {status === 'idle' && (
          <FileUploader onUploaded={handleUploaded} />
        )}

        {status === 'analyzing' && job && (
          <AnalyzePanel job={job} onAnalyzed={handleAnalyzed} onError={handleError} />
        )}

        {status === 'analyzed' && job && (
          <div>
            <div className="max-w-xl mx-auto text-center">
              <div className="text-green-600 text-lg mb-2">分析完成: {job.original_filename}</div>
            </div>
            <StructureDisplay structure={job.structure} warnings={job.warnings} />
            <div className="max-w-xl mx-auto mt-8 text-center">
              <button
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={() => { /* 下一步：排版 */ }}
              >
                开始排版
              </button>
            </div>
            <div className="text-center text-gray-400 text-sm mt-2">下一步：排版（待实现）</div>
          </div>
        )}

        {status === 'error' && (
          <div className="max-w-xl mx-auto mt-20 text-center">
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 mb-4">
              {error}
            </div>
            <button
              className="px-4 py-2 text-blue-600 hover:underline"
              onClick={() => { setStatus('idle'); setError(''); setJob(null); }}
            >
              重新开始
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
```

- [ ] **步骤 3.9：浏览器验证全流程**

打开 http://localhost:5173 → 上传论文 → 等待 AI 分析 → 确认章节结构正确显示

预期：上传完成后自动进入分析，30-60 秒后显示章节列表和警告

- [ ] **步骤 3.10：提交**

```bash
git add -A && git commit -m "feat: add AI analyzer — DeepSeek integration + frontend analysis flow"
```

---

### 任务 4：排版引擎（核心）

**文件：**
- 创建：`backend/app/modules/format_engine/__init__.py`
- 创建：`backend/app/modules/format_engine/matcher.py`
- 创建：`backend/app/modules/format_engine/applier.py`
- 创建：`backend/app/modules/format_engine/service.py`
- 创建：`backend/app/modules/format_engine/router.py`
- 修改：`backend/app/main.py` — 注册 format_engine router
- 创建：`frontend/src/components/ResultView.tsx`
- 修改：`frontend/src/App.tsx` — 添加排版+下载流程

- [ ] **步骤 4.1：创建 format_engine/matcher.py**

```python
"""Paragraph-to-section matching engine.

Three strategies (in order):
  Strategy 0: Paper title / subtitle / special headings
  Strategy 1: Exact heading match (numbering + title)
  Strategy 2: start_marker fallback for unmatched sections
"""
import re

SPECIAL_KEYWORDS = ["摘要", "Abstract", "关键词", "目录", "参考文献", "致谢", "附录"]


def match_paragraph(text: str, structure: dict, matched_sections: set) -> tuple:
    """
    Returns (match_type: str, level: int | None)

    match_type: "paper_title" | "subtitle" | "special_heading" | "heading" | "body" | "empty" | "toc"
    """
    clean = text.strip()
    if not clean:
        return ("empty", None)

    if _is_toc_entry(clean):
        return ("toc", None)

    sections = structure.get("sections", [])

    # Strategy 0a: Paper title
    title = structure.get("title", "")
    if title and "__title__" not in matched_sections and is_title_match(clean, title):
        matched_sections.add("__title__")
        return ("paper_title", 0)

    # Strategy 0b: Subtitle
    subtitle = structure.get("subtitle") or ""
    if subtitle and "__subtitle__" not in matched_sections and is_title_match(clean, subtitle):
        matched_sections.add("__subtitle__")
        return ("subtitle", 0)

    # Strategy 0c: Special headings — only if paragraph STARTS with keyword AND is short
    for kw in SPECIAL_KEYWORDS:
        if kw not in matched_sections and len(clean) <= 30 and clean.startswith(kw):
            matched_sections.add(kw)
            return ("special_heading", 0)

    # Strategy 1: Exact heading match (numbering + title)
    for sec in sections:
        numbering = sec.get("numbering", "")
        sec_title = sec.get("title", "")
        full = f"{numbering}{sec_title}" if numbering else sec_title
        if full and full not in matched_sections and is_title_match(clean, full):
            matched_sections.add(full)
            return ("heading", sec.get("level", 1))

    # Strategy 2: start_marker fallback
    for sec in sections:
        numbering = sec.get("numbering", "")
        sec_title = sec.get("title", "")
        full = f"{numbering}{sec_title}" if numbering else sec_title
        if full in matched_sections:
            continue
        marker = sec.get("start_marker", "")
        if marker and len(marker) >= 6 and marker in clean:
            if not _is_body_signal(marker):
                matched_sections.add(full)
                return ("heading", sec.get("level", 1))

    return ("body", None)


def is_title_match(para_text: str, title: str) -> bool:
    """Check if a paragraph text matches a title."""
    clean_para = para_text.strip().replace(" ", "")
    clean_title = title.strip().replace(" ", "")
    if not clean_para or not clean_title:
        return False
    # Exact match
    if clean_para == clean_title:
        return True
    # Paragraph starts with title (within 20 char)
    if clean_para.startswith(clean_title) and len(clean_para) - len(clean_title) <= 20:
        return True
    # Short paragraph (≤30 chars) contains title
    if len(clean_para) <= 30 and clean_title in clean_para:
        return True
    return False


def _is_toc_entry(text: str) -> bool:
    """Detect table-of-content entries with dot leaders."""
    if re.search(r"\.{3,}", text):
        return True
    if re.search(r"…{2,}", text):
        return True
    if re.search(r"\[页码\]", text):
        return True
    return False


def _is_body_signal(text: str) -> bool:
    """Check if text looks like body content rather than a heading."""
    body_starts = ["本文", "研究", "目前", "近年来", "随着", "根据", "通过", "在"]
    return any(text.startswith(w) for w in body_starts)
```

- [ ] **步骤 4.2：创建 format_engine/applier.py**

```python
"""Apply nursing-paper format specs to docx paragraphs."""
import re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.modules.format_standards.defaults import (
    get_page_spec, get_title_spec, get_subtitle_spec,
    get_special_heading_spec, get_heading_spec, get_body_spec,
    get_caption_spec, get_reference_spec,
)
from app.modules.format_standards.fonts import set_east_asian_font, set_latin_font


def _normalize_alignment(align_str: str) -> int | None:
    mapping = {
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    }
    return mapping.get(align_str)


def apply_page_spec(doc: Document) -> None:
    spec = get_page_spec()
    for section in doc.sections:
        section.top_margin = Cm(spec["margin_top_cm"])
        section.bottom_margin = Cm(spec["margin_bottom_cm"])
        section.left_margin = Cm(spec["margin_left_cm"])
        section.right_margin = Cm(spec["margin_right_cm"])


def _apply_run_font(run, font_name: str, font_size_pt: int, bold: bool):
    run.font.size = Pt(font_size_pt)
    run.bold = bold
    set_east_asian_font(run, font_name)
    text = run.text
    if text and re.search(r"[a-zA-Z0-9]", text) and match_type_needs_tnr:
        set_latin_font(run, "Times New Roman")
    else:
        set_latin_font(run, font_name)


# Track whether we need Times New Roman for Latin chars
match_type_needs_tnr = False


def apply_format(paragraph, match_type: str, level: int | None, in_reference: bool = False):
    """Apply format spec to a single paragraph based on match type."""
    global match_type_needs_tnr
    pf = paragraph.paragraph_format

    # Select the right spec
    if in_reference and match_type == "body":
        spec = get_reference_spec()
        match_type_needs_tnr = False
    elif match_type == "paper_title":
        spec = get_title_spec()
        match_type_needs_tnr = False
    elif match_type == "subtitle":
        spec = get_subtitle_spec()
        match_type_needs_tnr = False
    elif match_type == "special_heading":
        spec = get_special_heading_spec()
        match_type_needs_tnr = False
    elif match_type == "heading":
        spec = get_heading_spec(level or 1)
        match_type_needs_tnr = False
    elif match_type == "body":
        text = paragraph.text.strip()
        if re.match(r"^(图|表)\s*\d+", text):
            spec = get_caption_spec()
            match_type_needs_tnr = False
        elif in_reference:
            spec = get_reference_spec()
            match_type_needs_tnr = False
        else:
            spec = get_body_spec()
            match_type_needs_tnr = True  # TNR for Latin chars in body
    else:
        return

    # Alignment
    if "alignment" in spec:
        align = _normalize_alignment(spec["alignment"])
        if align is not None:
            pf.alignment = align

    # Line spacing
    if "line_spacing_pt" in spec:
        from docx.enum.text import WD_LINE_SPACING
        pf.line_spacing = Pt(spec["line_spacing_pt"])
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    elif "line_spacing" in spec:
        from docx.enum.text import WD_LINE_SPACING
        pf.line_spacing = spec["line_spacing"]
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE

    # First line indent (explicitly set to avoid inheritance)
    if "first_line_indent_chars" in spec:
        chars = spec["first_line_indent_chars"]
        font_size = spec.get("font_size_pt", 12)
        pf.first_line_indent = Pt(font_size * chars)
    else:
        pf.first_line_indent = Pt(0)

    # Space before/after
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    # Font on all runs
    font_name = spec.get("font_name", "宋体")
    font_size = spec.get("font_size_pt", 12)
    bold = spec.get("bold", False)

    for run in paragraph.runs:
        _apply_run_font(run, font_name, font_size, bold)
```

- [ ] **步骤 4.3：创建 format_engine/service.py**

```python
"""Format engine: orchestrate the formatting pipeline."""
from pathlib import Path
from docx import Document
from docx.shared import Pt
from app.modules.format_engine.matcher import match_paragraph, SPECIAL_KEYWORDS
from app.modules.format_engine.applier import apply_format, apply_page_spec


def execute(input_path: str, output_path: str, structure: dict) -> None:
    doc = Document(input_path)

    # Step 1: Apply page specs
    apply_page_spec(doc)

    # Step 2: Build sorted sections and determine reference boundary
    sections = structure.get("sections", [])
    matched_sections: set = set()
    in_reference = False

    # Step 3: Process each paragraph
    for para in doc.paragraphs:
        text = para.text

        # Skip table cells
        if para._element.getparent() is not None:
            parent_tag = para._element.getparent().tag
            if "tc" in parent_tag.split("}")[-1] if "}" in parent_tag else parent_tag:
                continue

        match_type, level = match_paragraph(text, structure, matched_sections)

        # Enter/exit reference mode
        if match_type == "special_heading" and "参考文献" in text:
            in_reference = True
        elif match_type in ("heading", "special_heading") and "参考文献" not in text:
            in_reference = False

        apply_format(para, match_type, level, in_reference)

    # Step 4: Save
    doc.save(output_path)
```

- [ ] **步骤 4.4：创建 format_engine/router.py**

```python
from fastapi import APIRouter
from app.shared.errors import NotFoundError, FormatError
from app.job_store import get_job, update_job
from app.modules.format_engine.service import execute
from pathlib import Path
from app.config import settings

router = APIRouter()


@router.post("/api/format/{job_id}")
async def format_paper(job_id: str):
    job = get_job(job_id)
    if not job:
        raise NotFoundError(message=f"任务 {job_id} 不存在")
    if not job.get("structure"):
        raise FormatError(message="请先完成 AI 分析再排版")

    update_job(job_id, status="formatting")

    output_dir = Path(settings.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{job_id}.docx"

    try:
        execute(job["file_path"], str(output_path), job["structure"])
    except Exception as e:
        update_job(job_id, status="error")
        raise FormatError(message=f"排版失败: {e}")

    update_job(job_id, status="done", output_path=str(output_path))

    return {
        "id": job_id,
        "original_filename": job["original_filename"],
        "file_type": job["file_type"],
        "status": "done",
        "download_url": f"/api/download/{job_id}",
    }
```

- [ ] **步骤 4.5：注册 format_engine router 到 main.py**

```python
from app.modules.format_engine.router import router as format_router
app.include_router(format_router)
```

- [ ] **步骤 4.6：curl 验证排版**

```bash
# 先上传和分析获取 job_id，然后：
curl -X POST "http://localhost:8000/api/format/$JOB_ID"
# 预期: {"id":"...", "status":"done", "download_url":"/api/download/..."}

# 下载验证：
curl -o /tmp/formatted.docx "http://localhost:8000/api/download/$JOB_ID"
# 用 Word 打开检查格式
```

- [ ] **步骤 4.7：创建前端 ResultView.tsx**

```typescript
import { getDownloadUrl } from '../services/api';

interface Props {
  jobId: string;
  filename: string;
}

export default function ResultView({ jobId, filename }: Props) {
  return (
    <div className="max-w-xl mx-auto mt-20 text-center">
      <div className="text-green-600 text-2xl mb-2">排版完成</div>
      <p className="text-gray-500 mb-8">{filename}</p>

      <a
        href={getDownloadUrl(jobId)}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg"
      >
        下载排版文件
      </a>

      <p className="text-sm text-gray-400 mt-4">
        点击下载后，浏览器会下载 .docx 文件，用 Word 打开即可查看
      </p>
    </div>
  );
}
```

- [ ] **步骤 4.8：更新 App.tsx 集成排版+下载**

在 `handleAnalyzed` 之后添加排版逻辑，完整流程：idle → uploaded(自动分析) → analyzed(点排版) → done(点下载)

关键变更：
```typescript
const handleFormat = async () => {
  if (!job) return;
  setStatus('formatting');
  try {
    const result = await apiFormat(job.id);
    setJob(result);
    setStatus('done');
  } catch (e: any) {
    setError(e.message || '排版失败');
    setStatus('error');
  }
};
```

在 analyzed 状态下显示"开始排版"按钮，点击后调用 handleFormat；done 状态下显示 ResultView。

- [ ] **步骤 4.9：浏览器端到端验证**

打开 http://localhost:5173 → 上传论文 → 等 AI 分析 → 点排版 → 下载文件 → 用 Word 打开验证格式

检查项：
1. 页面边距四边 2.5cm ✓
2. 标题层级字体字号加粗正确 ✓
3. 正文宋体小四 1.5 倍行距首行缩进 ✓
4. 英文数字 Times New Roman ✓

- [ ] **步骤 4.10：提交**

```bash
git add -A && git commit -m "feat: add format engine — matcher + applier + service + frontend download"
```

---

### 任务 5：前端打磨

**文件：**
- 创建：`frontend/src/components/StepIndicator.tsx`
- 修改：`frontend/src/App.tsx` — 添加步骤指示器、完善错误处理

- [ ] **步骤 5.1：创建 StepIndicator.tsx**

```typescript
import { AppStep } from '../types';

const STEPS: { key: AppStep; label: string }[] = [
  { key: 'upload', label: '上传论文' },
  { key: 'analyze', label: 'AI 分析' },
  { key: 'format', label: '自动排版' },
  { key: 'download', label: '下载文件' },
];

interface Props {
  current: AppStep;
}

export default function StepIndicator({ current }: Props) {
  const currentIdx = STEPS.findIndex((s) => s.key === current);

  return (
    <div className="flex justify-center gap-2 mb-8">
      {STEPS.map((step, i) => {
        const done = i < currentIdx;
        const active = i === currentIdx;

        return (
          <div key={step.key} className="flex items-center gap-2">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium
                ${done ? 'bg-green-500 text-white' : ''}
                ${active ? 'bg-blue-600 text-white' : ''}
                ${!done && !active ? 'bg-gray-200 text-gray-500' : ''}`}
            >
              {done ? '✓' : i + 1}
            </div>
            <span className={`text-xs ${active ? 'text-blue-600 font-medium' : 'text-gray-400'}`}>
              {step.label}
            </span>
            {i < STEPS.length - 1 && (
              <div className={`w-8 h-px ${i < currentIdx ? 'bg-green-400' : 'bg-gray-300'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **步骤 5.2：更新 App.tsx** — 在每个状态切换时更新 currentStep

- [ ] **步骤 5.3：浏览器最终验证**

完整走通 4 步：上传 → 分析 → 排版 → 下载。控制台无报错，下载文件格式正确。

- [ ] **步骤 5.4：提交**

```bash
git add -A && git commit -m "feat: add StepIndicator + final polish"
```

---

## 关键约束速查（所有任务遵守）

1. 后端所有返回 JSON 字段用 `"id"` 不是 `"job_id"`
2. 异常继承 `HTTPException`，不写 handler
3. 下载用 `Content-Disposition: attachment` + 前端 `target="_blank"`（不设 download 属性）
4. matcher Strategy 0c 用 `startswith` + 长度 ≤ 30
5. matcher 有 `_is_toc_entry()` 检测
6. applier 首行缩进显式设置，不依赖继承
7. 每步写完 → curl 测试 → 浏览器测试 → 再继续

---

## 验证记录

| 任务 | curl 通过 | 浏览器通过 | 备注 |
|------|----------|-----------|------|
| 0 脚手架 | — | — | |
| 1 格式标准 | — | — | |
| 2 文件处理 | | | |
| 3 AI 分析 | | | |
| 4 排版引擎 | | | |
| 5 前端打磨 | | | |
