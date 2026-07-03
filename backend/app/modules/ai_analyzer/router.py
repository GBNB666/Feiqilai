import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.job_manager.service import JobService
from app.modules.ai_analyzer.service import AIService
from app.modules.ai_analyzer.warnings import detect_warnings
from app.shared.schemas import JobResponse
from app.shared.errors import NotFoundError, AIError, RateLimitError

router = APIRouter(prefix="/api/format", tags=["ai"])

# 简易速率限制: 每 IP 每分钟最多 5 次分析
_rate_limit_store: dict[str, list[float]] = {}


def _check_rate_limit(ip: str, max_req: int = 5, window: float = 60.0) -> bool:
    now = time.time()
    bucket = _rate_limit_store.setdefault(ip, [])
    bucket[:] = [t for t in bucket if now - t < window]
    if len(bucket) >= max_req:
        return False
    bucket.append(now)
    return True


@router.post("/analyze")
async def analyze(job_id: str, db: Session = Depends(get_db), request: Request = None):
    # 速率限制
    client_ip = request.client.host if request else "unknown"
    if not _check_rate_limit(client_ip):
        raise RateLimitError()

    job = JobService.get(job_id, db)
    if job is None:
        raise NotFoundError(f"Job not found: {job_id}")
    # 并发防护：仅 UPLOADED 或 FAILED 状态可进入分析
    from app.shared.errors import ConflictError
    if job.status not in ("UPLOADED", "FAILED"):
        raise ConflictError(f"当前状态 {job.status} 不允许重复分析")

    try:
        JobService.set_status(job.id, "ANALYZING", db)
        structure = await AIService.analyze_file(job.file_path, job.file_type)
        JobService.save_analysis(job.id, structure, db)
        JobService.set_status(job.id, "ANALYZED", db)

        warnings = detect_warnings(structure)
    except Exception as e:
        JobService.set_status(job.id, "FAILED", db)
        raise AIError(f"AI分析失败: {str(e)}")

    job = JobService.get(job.id, db)
    response = JobService.to_response(job)
    response.warnings = warnings
    return response
