"""统一错误类型"""

class AppError(Exception):
    """应用基础异常"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class FileValidationError(AppError):
    """文件验证失败"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(AppError):
    """资源不存在"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class AIError(AppError):
    """AI分析失败"""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class FormatError(AppError):
    """排版处理失败"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
