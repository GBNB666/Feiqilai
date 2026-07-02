import json
import httpx
from app.config import get_settings
from app.modules.ai_analyzer.prompt import SYSTEM_PROMPT

_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0))
    return _http_client


async def close_http_client() -> None:
    """关闭全局 httpx 客户端（在 FastAPI lifespan shutdown 中调用）。"""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


class AIService:
    @staticmethod
    async def analyze(text: str) -> dict:
        """调用 DeepSeek API 分析论文结构，返回 structure dict。"""
        settings = get_settings()
        client = _get_client()

        response = await client.post(
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
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_json(content)

    @staticmethod
    async def analyze_file(file_path: str, file_type: str) -> dict:
        """从文件提取文本后调用 AI 分析。"""
        from app.modules.file_handler.extractors import extract_text
        text = extract_text(file_path, file_type)
        return await AIService.analyze(text)


def _parse_json(raw: str) -> dict:
    """解析 AI 返回的 JSON，失败时尝试修复截断。"""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 尝试统计括号，补齐缺失
    open_braces = raw.count("{")
    close_braces = raw.count("}")
    open_brackets = raw.count("[")
    close_brackets = raw.count("]")

    fixed = raw.rstrip()
    # 补齐缺失的 ]
    while open_brackets > close_brackets:
        fixed += "]"
        close_brackets += 1
    # 补齐缺失的 }
    while open_braces > close_braces:
        fixed += "}"
        close_braces += 1

    # 移除尾部可能残留的逗号（在 } 或 ] 前）
    fixed = fixed.rstrip()
    while fixed and fixed[-1] == ",":
        fixed = fixed[:-1]

    return json.loads(fixed)
