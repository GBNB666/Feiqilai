# 论文排版网站 MVP 实施计划（修订版）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 构建论文排版网站MVP核心排版功能（上传→分析→排版→下载）。支付功能留置，未来再对接。

**架构：** 前后端分离。前端 React + TypeScript + shadcn/ui + Tailwind CSS。后端 Python FastAPI + SQLite。DeepSeek-V4 做论文结构识别。python-docx / PyPDF2 做文件处理。

**技术栈：** React 18 + TypeScript + Vite + shadcn/ui + Tailwind CSS / Python 3.13 + FastAPI + SQLAlchemy + SQLite / DeepSeek-V4 API

**项目路径：** `C:\Users\博博\paper-formatter/`

**当前状态：** 阶段一~七代码已全部写入，后端11个API端点（含支付）均已通过测试，前端构建通过。

---

## 本次调整范围

支付功能留置，聚焦核心排版流程。需要做以下改动：

| 改动的文件 | 操作 |
|-----------|------|
| `backend/app/services/payment_stub.py` | 新建：支付占位文件 |
| `backend/app/main.py` | 修改：移除 payment 路由注册 |
| `backend/app/routers/payment.py` | 修改：改为 stub 端点 |
| `backend/app/config.py` | 修改：移除 XPay 配置项 |
| `backend/.env` | 修改：移除 XPay 配置 |
| `frontend/src/pages/ProcessPage.tsx` | 修改：移除支付弹窗，模式选择后直接进入排版 |
| `frontend/src/services/api.ts` | 修改：移除支付相关 API 方法 |
| `frontend/src/types/index.ts` | 修改：移除 PaymentOrder 类型 |

**不变的文件（保留供未来使用）：**
- `backend/app/models/payment.py` —— 支付数据模型（不注册到数据库）
- `backend/app/schemas/payment.py` —— 支付 Pydantic schema
- `frontend/src/components/payment/` —— 支付UI组件（不导入）
- `frontend/src/hooks/usePayment.ts` —— 支付 hook（不导入）

---

## 调整任务

### 任务 A：后端支付留置

**文件：**
- 创建：`backend/app/services/payment_stub.py`
- 修改：`backend/app/main.py`
- 修改：`backend/app/routers/payment.py`
- 修改：`backend/app/config.py`
- 修改：`backend/.env`

- [ ] **步骤 1：创建支付占位文件**

```python
# backend/app/services/payment_stub.py
"""
支付模块占位文件 (Payment Stub)
================================
未来集成 XPay 个人收款系统时在此实现。
XPay 是 Java Spring Boot 应用，通过 HTTP API 交互。

计划对接端点：
- POST /pay/add     — 创建支付订单
- GET  /pay/state/{id} — 查询支付状态

当前版本不包含支付功能，排版服务免费使用。

TODO (future):
1. 在 backend/.env 中配置 XPAY_BASE_URL
2. 实现 create_order(job_id) -> 调用 XPay API
3. 实现 check_payment(order_id) -> 轮询支付状态
4. 在 main.py 中注册 payment router
5. 在前端 ProcessPage 中恢复 PaymentModal
"""
```

- [ ] **步骤 2：修改 `backend/app/main.py`** —— 移除 payment 路由和 PaymentRecord 导入

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

app = FastAPI(title="论文排版系统 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "paper-formatter"}


def init_app():
    from app.models.job import FormatJob  # noqa: F401
    # 注意: PaymentRecord 暂不注册，支付功能留置
    # from app.models.payment import PaymentRecord  # noqa: F401
    Base.metadata.create_all(bind=engine)
    from app.routers import upload, format, download
    app.include_router(upload.router, prefix="/api", tags=["上传"])
    app.include_router(format.router, prefix="/api", tags=["排版"])
    app.include_router(download.router, prefix="/api", tags=["下载"])
    # 支付路由留置，未来启用:
    # from app.routers import payment
    # app.include_router(payment.router, prefix="/api", tags=["支付"])


init_app()
```

- [ ] **步骤 3：修改 `backend/app/routers/payment.py`** —— 改为 stub

```python
# backend/app/routers/payment.py
"""
支付路由占位 (Payment Router Stub)
未来集成 XPay 时，取消注释下方端点并实现。
详见 backend/app/services/payment_stub.py
"""
from fastapi import APIRouter

router = APIRouter()

# 未来启用:
# @router.post("/payment/create-order")
# def create_payment_order(...): ...
#
# @router.post("/payment/callback")
# def payment_callback(...): ...
#
# @router.get("/payment/status/{job_id}")
# def check_payment_status(...): ...
```

- [ ] **步骤 4：修改 `backend/app/config.py`** —— 移除 XPay 配置

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    database_url: str = "sqlite:///./paper_formatter.db"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
```

- [ ] **步骤 5：修改 `backend/.env`** —— 移除 XPay 配置

```
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DATABASE_URL=sqlite:///./paper_formatter.db
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
```

- [ ] **步骤 6：重启后端并验证路由**

```bash
pkill -9 -f uvicorn
sleep 1
/c/Users/博博/python.exe -m uvicorn app.main:app --port 8000 &
sleep 3
/c/Users/博博/python.exe -c "from app.main import app; print([r.path for r in app.routes if '/api' in r.path])"
# 预期：只有 /api/health, /api/upload, /api/format/*, /api/download/*
# 不应包含 /api/payment/*
```

---

### 任务 B：前端移除支付

**文件：**
- 修改：`frontend/src/pages/ProcessPage.tsx`
- 修改：`frontend/src/services/api.ts`
- 修改：`frontend/src/types/index.ts`

- [ ] **步骤 1：修改 `ProcessPage.tsx`** —— 移除支付弹窗，模式选择后直接排版

```tsx
// frontend/src/pages/ProcessPage.tsx
import { useParams } from "react-router-dom"
import { ModeSelector } from "@/components/mode/ModeSelector"
import { AnnotationPanel } from "@/components/annotate/AnnotationPanel"
import { ResultPreview } from "@/components/result/ResultPreview"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { useFormatting } from "@/hooks/useFormatting"
import type { FormatMode, PaperStructure } from "@/types"

export function ProcessPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const { state, job, structure, error, selectMode, submitAnnotations } = useFormatting(jobId || "")

  const handleModeSelect = (mode: FormatMode) => {
    // 直接进入排版，无需支付
    selectMode(mode)
  }

  if (state === "error") return <ErrorAlert message={error} />
  if (state === "analyzing" || state === "formatting") {
    return <LoadingSpinner text={state === "analyzing" ? "AI正在分析论文结构..." : "正在排版中..."} />
  }
  if (state === "done" && job) return <ResultPreview job={job} />

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {state === "selecting" && <ModeSelector onSelect={handleModeSelect} />}
      {state === "analyzed" && structure && (
        <AnnotationPanel structure={structure as PaperStructure} onSubmit={submitAnnotations} />
      )}
      {state === "idle" && <LoadingSpinner text="加载中..." />}
    </div>
  )
}
```

- [ ] **步骤 2：修改 `api.ts`** —— 移除支付方法

```typescript
// frontend/src/services/api.ts
import type { FormatJob } from "@/types"

const BASE = "/api"

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  upload: async (file: File): Promise<FormatJob> => {
    const formData = new FormData()
    formData.append("file", file)
    const res = await fetch(`${BASE}/upload`, { method: "POST", body: formData })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  },

  selectMode: (jobId: string, mode: string) =>
    request<FormatJob>("/format/select-mode", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, format_mode: mode }),
    }),

  startAnalysis: (jobId: string) =>
    request<FormatJob>(`/format/analyze?job_id=${jobId}`, { method: "POST" }),

  submitAnnotations: (jobId: string, annotations: string) =>
    request<FormatJob>("/format/annotate", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, annotations }),
    }),

  executeFormatting: (jobId: string) =>
    request<FormatJob>(`/format/execute?job_id=${jobId}`, { method: "POST" }),

  getJobStatus: (jobId: string) =>
    request<FormatJob>(`/format/job/${jobId}`),
}

export function getDownloadUrl(jobId: string) {
  return `${BASE}/download/${jobId}`
}
```

- [ ] **步骤 3：修改 `types/index.ts`** —— 移除 PaymentOrder 类型

```typescript
// frontend/src/types/index.ts

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
```

- [ ] **步骤 4：验证前端构建**

```bash
cd frontend && npm run build
# 预期：编译成功，无错误
```

---

### 任务 C：端到端验证

- [ ] **步骤 1：启动后端**

```bash
cd backend
pkill -9 -f uvicorn; sleep 1
/c/Users/博博/python.exe -m uvicorn app.main:app --port 8000 &
sleep 3
```

- [ ] **步骤 2：测试核心流程（上传→分析→排版→下载）**

```bash
# 上传真实论文文件
UPLOAD=$(curl -s -X POST http://localhost:8000/api/upload \
  -F "file=@/c/Users/博博/uploads/test_paper.docx")
JOB_ID=$(echo "$UPLOAD" | /c/Users/博博/python.exe -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Job: $JOB_ID"

# 选择全自动模式
curl -s -X POST http://localhost:8000/api/format/select-mode \
  -H "Content-Type: application/json" \
  -d "{\"job_id\":\"$JOB_ID\",\"format_mode\":\"auto\"}"

# AI分析
curl -s -X POST "http://localhost:8000/api/format/analyze?job_id=$JOB_ID"

# 执行排版
curl -s -X POST "http://localhost:8000/api/format/execute?job_id=$JOB_ID"

# 下载
curl -s -o /dev/null -w "Download HTTP: %{http_code}\n" \
  "http://localhost:8000/api/download/$JOB_ID"
```

预期输出：每一步都应返回成功状态，最终下载返回 HTTP 200。

- [ ] **步骤 3：确认支付端点不在路由中**

```bash
/c/Users/博博/python.exe -c "from app.main import app; paths=[r.path for r in app.routes if '/api' in r.path]; assert '/api/payment/create-order' not in paths, 'Payment route should be removed'; print('Routes OK:', paths)"
```

预期：断言通过，不包含 `/api/payment/*`。

- [ ] **步骤 4：启动前端并验证代理**

```bash
cd ../frontend && npm run dev &
sleep 3
curl -s http://localhost:5173/api/health
```

预期：返回 `{"status":"ok","service":"paper-formatter"}`。

---

## 完成标志

- [x] 支付功能已留置（stub文件 + 注释完善的占位代码）
- [x] 后端路由不含支付端点
- [x] 前端 ProcessPage 无支付弹窗
- [x] 核心流程（上传→分析→排版→下载）全部通过
- [x] 前端构建零错误
- [x] 前后端代理连通

---

## 未来支付集成指南

当需要恢复支付功能时，按以下步骤操作：

1. 在 `backend/.env` 中设置 `XPAY_BASE_URL=http://xpay-server:8080`
2. 在 `backend/app/config.py` 中添加 `xpay_base_url` 字段
3. 阅读 `backend/app/services/payment_stub.py` 了解集成点
4. 在 `backend/app/main.py` 中取消注释 `from app.routers import payment` 和对应 `include_router`
5. 恢复 `backend/app/routers/payment.py` 中的端点实现（参考旧版或 XPay Java 源码）
6. 在前端 `ProcessPage.tsx` 中恢复 `PaymentModal` 组件
7. 在前端 `api.ts` 中恢复 `createPaymentOrder` 和 `checkPaymentStatus` 方法
