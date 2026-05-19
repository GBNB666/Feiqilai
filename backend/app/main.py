"""FastAPI 应用入口"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base


def create_app() -> FastAPI:
    app = FastAPI(title="论文排版系统 API", version="0.2.0")

    origins = [o.strip() for o in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "service": "paper-formatter", "version": "0.2.0"}

    # 注册自定义异常处理器，将 AppError 转为 HTTP 响应
    from app.shared.errors import AppError
    from fastapi.responses import JSONResponse
    from fastapi import Request

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    return app


def init_app(app: FastAPI) -> None:
    """初始化：创建目录、建表、注册路由、种子数据"""
    # 创建必要目录
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

    # 创建数据库表
    from app.modules.job_manager.models import FormatJob  # noqa: F401
    from app.modules.template_manager.models import FormatTemplate  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # 注册路由
    from app.modules.file_handler.router import router as file_router
    app.include_router(file_router)
    from app.modules.ai_analyzer.router import router as ai_router
    app.include_router(ai_router)
    from app.modules.format_engine.router import router as format_router
    app.include_router(format_router)
    from app.modules.preview.router import router as preview_router
    app.include_router(preview_router)
    from app.modules.job_manager.router import router as job_router
    app.include_router(job_router)
    from app.modules.template_manager.router import router as template_router
    app.include_router(template_router)

    # 种子数据
    from app.modules.template_manager.service import TemplateService
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        TemplateService.seed_default(db)
    finally:
        db.close()


app = create_app()
init_app(app)
