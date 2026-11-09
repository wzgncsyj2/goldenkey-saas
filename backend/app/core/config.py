"""
核心配置模块
============
支持多环境配置：dev / test / prod

使用方式:
    # 开发环境（默认）
    python run.py
    
    # 测试环境
    APP_ENV=test python run.py
    
    # 生产环境
    APP_ENV=prod python run.py
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
import structlog


# ============================================================
# 环境检测
# ============================================================

def get_env_file() -> Path:
    """根据 APP_ENV 返回对应的配置文件路径"""
    env = os.getenv("APP_ENV", "dev").lower()
    
    # 映射环境名到文件名
    env_map = {
        "dev": ".env.dev",
        "development": ".env.dev",
        "test": ".env.test",
        "testing": ".env.test",
        "prod": ".env.prod",
        "production": ".env.prod",
    }
    
    filename = env_map.get(env, ".env.dev")
    
    # 配置文件在 backend/config/ 目录下
    config_dir = Path(__file__).parent.parent.parent / "config"
    env_file = config_dir / filename
    
    # 如果配置文件不存在，尝试 backend/ 根目录的 .env
    if not env_file.exists():
        fallback = Path(__file__).parent.parent.parent / ".env"
        if fallback.exists():
            return fallback
    
    return env_file


# ============================================================
# 配置类
# ============================================================

class Settings(BaseSettings):
    """应用全局配置"""
    
    model_config = SettingsConfigDict(
        env_file=str(get_env_file()),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # --- 应用 ---
    APP_NAME: str = "金钥匙智知"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # --- 服务 ---
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # --- 数据库 ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    
    # --- Redis ---
    REDIS_URL: str = ""
    
    # --- JWT ---
    SECRET_KEY: str = "change-me-to-a-random-string-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # --- LLM ---
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    
    # --- Embedding ---
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = "https://api.openai.com/v1"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # --- 向量数据库 ---
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    
    # --- 文件存储 ---
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50
    
    # --- 租户配额 ---
    FREE_MAX_DOCUMENTS: int = 10
    FREE_MAX_STORAGE_MB: int = 100
    FREE_MAX_API_CALLS_PER_DAY: int = 100
    
    # --- CORS ---
    CORS_ORIGINS: List[str] = ["*"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @model_validator(mode="after")
    def validate_production_settings(self):
        """生产环境安全检查"""
        if self.APP_ENV in ("prod", "production"):
            if self.SECRET_KEY == "change-me-to-a-random-string-in-production":
                raise ValueError(
                    "生产环境必须设置 SECRET_KEY！"
                    "请通过环境变量注入: SECRET_KEY=<64位随机字符串>"
                )
            if self.DEBUG:
                raise ValueError("生产环境不能开启 DEBUG！")
        return self
    
    # --- 计算属性 ---
    @property
    def UPLOAD_PATH(self) -> Path:
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def DATA_PATH(self) -> Path:
        path = Path("./data")
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def is_production(self) -> bool:
        return self.APP_ENV in ("prod", "production")
    
    @property
    def is_development(self) -> bool:
        return self.APP_ENV in ("dev", "development")
    
    @property
    def is_test(self) -> bool:
        return self.APP_ENV in ("test", "testing")
    
    @property
    def logger(self):
        return structlog.get_logger()
    
    def __repr__(self) -> str:
        return (
            f"Settings(APP_ENV={self.APP_ENV}, "
            f"DEBUG={self.DEBUG}, "
            f"DATABASE_URL={'***' if 'password' in self.DATABASE_URL else self.DATABASE_URL})"
        )


# ============================================================
# 全局单例
# ============================================================

settings = Settings()

# 启动时打印配置信息
print(f"📋 配置加载: APP_ENV={settings.APP_ENV}, 配置文件={get_env_file()}")
