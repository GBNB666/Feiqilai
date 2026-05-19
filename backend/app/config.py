"""应用配置，从环境变量/.env加载"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    database_url: str = "sqlite:///./paper_formatter.db"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    cors_origins: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# 启动时校验
if not settings.deepseek_api_key:
    import sys
    print("[WARNING] DEEPSEEK_API_KEY 未设置，AI分析功能将不可用", file=sys.stderr)
