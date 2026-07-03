import os
import sys
from pydantic_settings import BaseSettings
from functools import lru_cache


def _default_data_dir() -> str:
    """exe 模式: %APPDATA%/AI智排/; 开发模式: 项目根目录"""
    if getattr(sys, "frozen", False):
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AI智排")
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    # ── AI ──
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # ── 数据目录（exe 模式下自动使用 %APPDATA%/AI智排）──
    data_dir: str = ""

    # ── 路径（基于 data_dir）──
    upload_dir: str = ""
    output_dir: str = ""
    database_url: str = ""

    # ── 服务器 ──
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:8000"

    # ── 静态文件 serve（exe 模式默认开）──
    serve_static: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        data = self.data_dir or _default_data_dir()
        os.makedirs(data, exist_ok=True)
        self.upload_dir = self.upload_dir or os.path.join(data, "uploads")
        self.output_dir = self.output_dir or os.path.join(data, "outputs")
        self.database_url = self.database_url or f"sqlite:///{os.path.join(data, 'paper_formatter.db')}"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.deepseek_api_key:
        print("WARNING: DEEPSEEK_API_KEY is empty. AI analysis will not work.")
    return settings
