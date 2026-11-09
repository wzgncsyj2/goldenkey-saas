"""
健康检查路由
"""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def root():
    """API 根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
