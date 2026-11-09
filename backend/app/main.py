"""
FastAPI 应用入口
================
创建 FastAPI 实例，注册路由，配置中间件。
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.exceptions import register_exception_handlers
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    configure_logging()
    settings.logger.info("application.starting", app_name=settings.APP_NAME)
    
    await init_db()
    settings.logger.info("database.initialized")
    
    yield
    
    settings.logger.info("application.stopping")


def create_application() -> FastAPI:
    """创建并配置 FastAPI 应用"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="企业级AI知识库+在线客服SaaS平台 API",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册异常处理
    register_exception_handlers(app)
    
    # 注册路由
    from app.api.routes import health, auth, documents, chat, tenants
    app.include_router(health.router, tags=["健康检查"])
    app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
    app.include_router(documents.router, prefix="/api/documents", tags=["文档"])
    app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
    app.include_router(tenants.router, prefix="/api/tenants", tags=["租户"])
    
    return app


app = create_application()
