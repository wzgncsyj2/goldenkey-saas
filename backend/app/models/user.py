"""
用户模型
========
支持多角色：超级管理员、租户管理员、普通用户、客服。
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, PyEnum):
    """用户角色"""
    SUPER_ADMIN = "super_admin"   # 平台超级管理员
    TENANT_ADMIN = "tenant_admin" # 租户管理员
    AGENT = "agent"               # 客服
    USER = "user"                 # 普通用户


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    
    # 基本信息
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="显示名称")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # 认证
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # 角色与状态
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, comment="用户角色"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # 关系
    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user")


# 避免循环导入
from app.models.tenant import Tenant
from app.models.conversation import Conversation
