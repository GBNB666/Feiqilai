import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import get_settings
from app.database import engine, Base


def _find_static_dir() -> str | None:
    """查找前端构建产物的目录。优先级:
    1. PyInstaller 打包路径: sys._MEIPASS/static/
    2. 生产模式: backend/static/ (__file__ 在 backend/app/ 下)
    3. 开发模式: frontend/dist/
    """
    import sys
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(os.path.join(sys._MEIPASS, "static"))  # type: ignore
    # backend/app/main.py → backend/static/
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(backend_dir, "static"))
    # 项目根 → frontend/dist/
    project_dir = os.path.dirname(backend_dir)
    candidates.append(os.path.join(project_dir, "frontend", "dist"))
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "index.html")):
            return c
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时初始化，关闭时清理。"""
    init_app(app)
    yield
    # 关闭 httpx client
    try:
        from app.modules.ai_analyzer.service import close_http_client
        await close_http_client()
    except Exception:
        pass


def create_app() -> FastAPI:
    app = FastAPI(title="AI智排", version="3.0.0", lifespan=lifespan)
    settings = get_settings()

    # ── CORS ──
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    # ── API 路由 ──
    from app.modules.file_handler.router import router as file_router
    from app.modules.job_manager.router import router as job_router
    from app.modules.ai_analyzer.router import router as ai_router
    from app.modules.format_engine.router import router as format_router
    from app.modules.preview.router import router as preview_router
    from app.modules.template_manager.router import router as template_router
    from app.modules.image_formatter.router import router as image_router
    from app.modules.school_template.router import router as school_template_router

    app.include_router(file_router)
    app.include_router(job_router)
    app.include_router(ai_router)
    app.include_router(format_router)
    app.include_router(preview_router)
    app.include_router(template_router)
    app.include_router(image_router)
    app.include_router(school_template_router)

    # ── 异常处理器 ──
    from app.shared.errors import register_exception_handlers
    register_exception_handlers(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # ── 前端静态文件（生产模式）──
    static_dir = _find_static_dir()
    if static_dir and settings.serve_static:
        assets_dir = os.path.join(static_dir, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str):
            """SPA fallback: 所有非 API 路径返回 index.html"""
            index_path = os.path.join(static_dir, "index.html")
            if os.path.isfile(index_path):
                return FileResponse(index_path)
            return {"detail": "Frontend not found"}, 404

    return app


def init_app(app: FastAPI) -> None:
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)

    from app.modules.job_manager.models import FormatJob  # noqa: F401
    from app.modules.template_manager.models import FormatTemplate  # noqa: F401
    Base.metadata.create_all(bind=engine)

    from app.database import SessionLocal
    from app.modules.template_manager.service import TemplateService
    with SessionLocal() as db:
        TemplateService.seed_default(db)


app = create_app()
