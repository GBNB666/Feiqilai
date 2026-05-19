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


def _seed_default_template():
    """Create the system default template if it does not exist."""
    from app.database import SessionLocal
    from app.models.template import FormatTemplate
    from app.schemas.job import FormatSettings
    db = SessionLocal()
    try:
        existing = db.query(FormatTemplate).filter(FormatTemplate.name == "系统默认").first()
        if not existing:
            default = FormatSettings()
            tmpl = FormatTemplate(name="系统默认", settings_json=default.model_dump_json())
            db.add(tmpl)
            db.commit()
    finally:
        db.close()


def init_app():
    from app.models.job import FormatJob  # noqa: F401
    from app.models.template import FormatTemplate  # noqa: F401
    Base.metadata.create_all(bind=engine)
    from app.routers import upload, format, download, preview, template
    app.include_router(upload.router, prefix="/api", tags=["上传"])
    app.include_router(format.router, prefix="/api", tags=["排版"])
    app.include_router(download.router, prefix="/api", tags=["下载"])
    app.include_router(preview.router, prefix="/api", tags=["预览"])
    app.include_router(template.router, prefix="/api", tags=["模板"])
    _seed_default_template()


init_app()
