"""
对话模型
========
客服对话和消息记录。
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationStatus(str, PyEnum):
    """对话状态"""
    ACTIVE = "active"         # 进行中
    WAITING = "waiting"       # 等待人工接入
    TRANSFERRED = "transferred"  # 已转人工
    CLOSED = "closed"         # 已关闭


class MessageRole(str, PyEnum):
    """消息角色"""
    USER = "user"     # 访客/用户
    AI = "ai"         # AI助手
    AGENT = "agent"   # 人工客服
    SYSTEM = "system" # 系统消息


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    # 访客信息 (未登录用户)
    visitor_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True, comment="访客标识(Cookie)")
    visitor_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="访客姓名")
    visitor_email: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="访客邮箱")
    
    # 对话信息
    subject: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="对话主题")
    status: Mapped[ConversationStatus] = mapped_column(
        String(20), default=ConversationStatus.ACTIVE, comment="对话状态"
    )
    
    # 人工客服
    assigned_agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="分配的客服ID")
    
    # 满意度
    satisfaction_rating: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="满意度评分(1-5)")
    satisfaction_comment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="满意度评价")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # 关系
    tenant: Mapped["Tenant"] = relationship(back_populates="conversations")
    user: Mapped["User | None"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    
    # 消息内容
    role: Mapped[MessageRole] = mapped_column(String(20), nullable=False, comment="消息角色")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    
    # 来源引用 (RAG)
    sources: Mapped[str | None] = mapped_column(Text, nullable=True, comment="引用来源(JSON)")
    
    # 状态
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已读")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# 避免循环导入
from app.models.tenant import Tenant
from app.models.user import User
