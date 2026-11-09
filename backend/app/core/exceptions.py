"""
异常处理模块
============
统一异常类和全局异常处理器。
"""

from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
import structlog

logger = structlog.get_logger()


# ============================================================
# 自定义异常类
# ============================================================

class GoldenKeyException(Exception):
    """金钥匙基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class AuthenticationError(GoldenKeyException):
    """认证失败"""
    def __init__(self, message: str = "认证失败，请重新登录"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class AuthorizationError(GoldenKeyException):
    """权限不足"""
    def __init__(self, message: str = "权限不足，无法执行此操作"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)


class NotFoundError(GoldenKeyException):
    """资源不存在"""
    def __init__(self, resource: str = "资源", id: Any = None):
        message = f"{resource}不存在" if not id else f"{resource} (ID: {id}) 不存在"
        super().__init__(message, "NOT_FOUND", 404)


class ValidationError(GoldenKeyException):
    """数据验证失败"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR", 422, details)


class QuotaExceededError(GoldenKeyException):
    """配额超限"""
    def __init__(self, resource: str, limit: int, current: int):
        message = f"{resource}已达上限 ({current}/{limit})"
        super().__init__(message, "QUOTA_EXCEEDED", 429)


class TenantNotActiveError(GoldenKeyException):
    """租户未激活"""
    def __init__(self, message: str = "租户账号未激活或已过期"):
        super().__init__(message, "TENANT_NOT_ACTIVE", 403)


# ============================================================
# 全局异常处理器
# ============================================================

def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(GoldenKeyException)
    async def goldenkey_exception_handler(request: Request, exc: GoldenKeyException):
        logger.warning(
            "business_error",
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled_exception",
            error=str(exc),
            path=request.url.path,
            exc_info=True,
        )
        return ORJSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误，请稍后重试",
                }
            },
        )
