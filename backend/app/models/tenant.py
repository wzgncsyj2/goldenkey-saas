"""
租户模型
========
多租户SaaS的核心，每个企业客户是一个租户。
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, DateTime, Boolean, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TenantPlan(str, PyEnum):
    """租户套餐"""
    FREE = "free"           # 免费版
    BASIC = "basic"         # 基础版
    PRO = "pro"             # 专业版
    ENTERPRISE = "enterprise"  # 企业版


class TenantStatus(str, PyEnum):
    """租户状态"""
    ACTIVE = "active"       # 正常
    TRIAL = "trial"         # 试用中
    SUSPENDED = "suspended" # 已暂停
    EXPIRED = "expired"     # 已过期


class Tenant(Base):
    """租户（企业）表"""
    __tablename__ = "tenants"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="企业名称")
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="租户标识符(用于URL)")
    domain: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True, comment="自定义域名")
    
    # 套餐与状态
    plan: Mapped[TenantPlan] = mapped_column(
        Enum(TenantPlan), default=TenantPlan.FREE, comment="当前套餐"
    )
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus), default=TenantStatus.TRIAL, comment="租户状态"
    )
    
    # 配额
    max_documents: Mapped[int] = mapped_column(Integer, default=10, comment="最大文档数")
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=100, comment="最大存储空间(MB)")
    max_api_calls_per_day: Mapped[int] = mapped_column(Integer, default=100, comment="每日API调用上限")
    
    # 使用情况
    current_storage_mb: Mapped[int] = mapped_column(Integer, default=0, comment="当前使用存储(MB)")
    api_calls_today: Mapped[int] = mapped_column(Integer, default=0, comment="今日API调用数")
    api_calls_reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="API调用计数重置时间")
    
    # 品牌配置 (JSON)
    branding: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="品牌配置(logo/颜色等)")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="试用到期时间")
    plan_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="套餐到期时间")
    
    # 关系
    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


# 避免循环导入
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation
