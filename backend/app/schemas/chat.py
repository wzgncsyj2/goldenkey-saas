"""
对话相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class ChatRequest(BaseModel):
    """对话请求"""
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    message: str = Field(..., min_length=1, max_length=5000)
    top_k: int = Field(5, ge=1, le=20)


class SatisfactionRequest(BaseModel):
    """满意度评价请求"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


# ============================================================
# 响应模型
# ============================================================

class ConversationResponse(BaseModel):
    """对话信息响应"""
    id: int
    tenant_id: int
    user_id: Optional[int] = None
    visitor_id: Optional[str] = None
    subject: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    conversation_id: int
    role: str
    content: str
    sources: Optional[str] = None
    is_read: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """对话回答响应"""
    question: str
    answer: str
    sources: List[dict]
    source_count: int


class ConversationDetailResponse(BaseModel):
    """对话详情响应（含消息）"""
    conversation: ConversationResponse
    messages: List[MessageResponse]
