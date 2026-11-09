"""
启动脚本
========
用于开发环境启动 FastAPI 应用。

使用方式:
    python run.py
    
或者:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn
from app.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
