"""
对话路由
========
创建对话、发送消息、流式回答、满意度评价。
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.dependencies import CurrentUser, TenantID, DBSession
from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation, Message, ConversationStatus, MessageRole
from app.models.user import User
from app.schemas.chat import (
    ConversationResponse,
    MessageResponse,
    ChatRequest,
    ChatResponse,
    SendMessageRequest,
    SatisfactionRequest,
    ConversationDetailResponse,
)

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """创建新对话"""
    conversation = Conversation(
        tenant_id=tenant_id,
        user_id=current_user["user_id"],
        status=ConversationStatus.ACTIVE,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return ConversationResponse.model_validate(conversation)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.tenant_id == tenant_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return [ConversationResponse.model_validate(conv) for conv in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取对话详情（含消息）"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise NotFoundError("对话", conversation_id)
    
    # 获取消息
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()
    
    return ConversationDetailResponse(
        conversation=ConversationResponse.model_validate(conversation),
        messages=[MessageResponse.model_validate(msg) for msg in messages],
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """删除对话"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise NotFoundError("对话", conversation_id)
    
    await db.delete(conversation)
    await db.commit()


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """
    发送消息并获取AI回答（非流式）
    """
    # 验证对话存在
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise NotFoundError("对话", conversation_id)
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)
    
    # TODO: 调用 RAG 服务获取回答
    ai_answer = f"这是对您问题 '{request.message}' 的模拟回答。"
    sources = []
    
    # 保存AI消息
    ai_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.AI,
        content=ai_answer,
        sources=json.dumps(sources) if sources else None,
    )
    db.add(ai_message)
    await db.commit()
    
    return ChatResponse(
        question=request.message,
        answer=ai_answer,
        sources=sources,
        source_count=len(sources),
    )


@router.post("/conversations/{conversation_id}/stream")
async def send_message_stream(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """
    发送消息并获取AI回答（SSE流式）
    """
    # 验证对话存在
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise NotFoundError("对话", conversation_id)
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)
    await db.commit()
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """生成 SSE 事件流"""
        # 发送来源事件
        sources = []
        yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
        
        # TODO: 调用 RAG 流式服务
        # 模拟逐字输出
        full_answer = f"这是对您问题 '{request.message}' 的流式回答。"
        
        for char in full_answer:
            yield f"data: {json.dumps({'type': 'delta', 'data': char})}\n\n"
        
        # 发送完成事件
        yield f"data: {json.dumps({'type': 'done', 'data': full_answer})}\n\n"
        
        # 保存AI消息
        ai_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.AI,
            content=full_answer,
        )
        db.add(ai_message)
        await db.commit()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


@router.post("/conversations/{conversation_id}/satisfaction")
async def rate_conversation(
    conversation_id: int,
    request: SatisfactionRequest,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """评价对话满意度"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise NotFoundError("对话", conversation_id)
    
    conversation.satisfaction_rating = request.rating
    conversation.satisfaction_comment = request.comment
    conversation.status = ConversationStatus.CLOSED
    await db.commit()
    
    return {"message": "评价成功"}
