"""
文档模型
========
知识库文档，支持多种格式。
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocumentStatus(str, PyEnum):
    """文档处理状态"""
    PENDING = "pending"           # 待处理
    PROCESSING = "processing"     # 处理中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 处理失败


class Document(Base):
    """文档表"""
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    
    # 文件信息
    filename: Mapped[str] = mapped_column(String(200), nullable=False, comment="原始文件名")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="服务器存储路径")
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件扩展名")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小(字节)")
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="MIME类型")
    
    # 处理状态
    status: Mapped[DocumentStatus] = mapped_column(
        String(20), default=DocumentStatus.PENDING, comment="处理状态"
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    
    # 切片统计
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, comment="切片数量")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="处理完成时间")
    
    # 元数据
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="标签(逗号分隔)")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="文档描述")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    tenant: Mapped["Tenant"] = relationship(back_populates="documents")


# 避免循环导入
from app.models.tenant import Tenant
