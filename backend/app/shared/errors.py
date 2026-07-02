"""统一异常体系 + FastAPI 异常处理器注册。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """应用级异常基类。"""
    def __init__(self, message: str, detail: str = "", status_code: int = 500):
        self.message = message
        self.detail = detail or message
        self.status_code = status_code
        super().__init__(message)


class FileValidationError(AppError):
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail, status_code=400)


class AIError(AppError):
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail, status_code=500)


class FormatError(AppError):
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail, status_code=500)


class NotFoundError(AppError):
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message, detail, status_code=409)


class RateLimitError(AppError):
    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(message, message, status_code=429)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器，统一错误响应格式。"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.status_code},
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "资源不存在", "code": 404},
        )
