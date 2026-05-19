"""AI 论文结构分析服务"""
import json
import httpx
from app.config import settings
from app.modules.file_handler.service import FileService
from app.modules.ai_analyzer.prompt import SYSTEM_PROMPT

_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(timeout=120.0)
    return _client


class AIService:
    @staticmethod
    def analyze(file_path: str, file_type: str) -> dict:
        """调用 DeepSeek API 分析论文结构"""
        text = FileService.extract_text(file_path, file_type)
        if not text.strip():
            raise ValueError("文档无可提取文本")

        client = _get_client()
        response = client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
                "max_tokens": 4096,
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_json(content)

    @staticmethod
    def detect_warnings(structure: dict) -> dict:
        from app.modules.ai_analyzer.warnings import detect_warnings
        return detect_warnings(structure)


def _parse_json(content: str) -> dict:
    """解析 AI 返回的 JSON，失败则尝试修复截断"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # 修复截断：补齐 } 和 ]
    open_braces = content.count("{") - content.count("}")
    open_brackets = content.count("[") - content.count("]")
    content += "]" * open_brackets + "}" * open_braces
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI 返回内容无法解析为 JSON: {e}") from e
