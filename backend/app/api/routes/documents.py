"""
文档路由
========
文档上传、列表、删除、处理、搜索。
"""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Query
from sqlalchemy import select, func

from app.core.dependencies import CurrentUser, TenantID, DBSession
from app.core.exceptions import NotFoundError, ValidationError, QuotaExceededError
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.tenant import Tenant
from app.schemas.document import (
    DocumentResponse,
    DocumentProcessResponse,
    SearchRequest,
    SearchResponse,
    DocumentStatsResponse,
)

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    tenant_id: TenantID = None,
    db: DBSession = None,
):
    """
    上传文档
    
    支持格式: PDF, DOCX, XLSX, PPTX, CSV, TXT, MD
    """
    # 检查文件类型
    allowed_types = {".pdf", ".docx", ".xlsx", ".pptx", ".csv", ".txt", ".md"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_types:
        raise ValidationError(f"不支持的文件类型: {file_ext}")
    
    # 检查文件大小
    content = await file.read()
    file_size = len(content)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise ValidationError(f"文件大小超过限制 ({settings.MAX_FILE_SIZE_MB}MB)")
    
    # 检查租户配额
    tenant = await db.get(Tenant, tenant_id)
    doc_count = await db.execute(
        select(func.count(Document.id)).where(Document.tenant_id == tenant_id)
    )
    if doc_count.scalar() >= tenant.max_documents:
        raise QuotaExceededError("文档数量", tenant.max_documents, doc_count.scalar())
    
    # 保存文件
    upload_dir = settings.UPLOAD_PATH / str(tenant_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = upload_dir / unique_name
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 创建文档记录
    document = Document(
        tenant_id=tenant_id,
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_ext,
        file_size=file_size,
        mime_type=file.content_type,
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return DocumentResponse.model_validate(document)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取当前租户的文档列表"""
    result = await db.execute(
        select(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取单个文档详情"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundError("文档", document_id)
    
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """删除文档"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundError("文档", document_id)
    
    # 删除物理文件
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # TODO: 删除 ChromaDB 中的向量数据
    
    # 删除数据库记录
    await db.delete(document)
    await db.commit()


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    document_id: int,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """
    处理文档
    
    解析 → 切片 → Embedding → 存入向量数据库
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundError("文档", document_id)
    
    if document.status == DocumentStatus.PROCESSING:
        raise ValidationError("文档正在处理中，请稍后再试")
    
    # 更新状态为处理中
    document.status = DocumentStatus.PROCESSING
    await db.commit()
    
    try:
        # TODO: 调用文档处理服务
        # 1. 解析文档
        # 2. 切片
        # 3. Embedding
        # 4. 存入 ChromaDB
        
        # 模拟处理结果
        document.status = DocumentStatus.COMPLETED
        document.chunk_count = 10
        document.processed_at = func.now()
        await db.commit()
        await db.refresh(document)
        
        return DocumentProcessResponse(
            document_id=document.id,
            filename=document.filename,
            text_length=5000,
            chunk_count=10,
            embedding_dim=1536,
            sample_chunks=["示例文本块1", "示例文本块2", "示例文本块3"],
        )
        
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        await db.commit()
        raise


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """在知识库中搜索"""
    # TODO: 调用向量搜索服务
    return SearchResponse(
        query=request.query,
        result_count=0,
        results=[],
    )


@router.get("/stats", response_model=DocumentStatsResponse)
async def get_document_stats(
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取文档统计信息"""
    # 总数
    total_result = await db.execute(
        select(func.count(Document.id)).where(Document.tenant_id == tenant_id)
    )
    document_count = total_result.scalar() or 0
    
    # 切片总数
    chunks_result = await db.execute(
        select(func.sum(Document.chunk_count)).where(Document.tenant_id == tenant_id)
    )
    total_chunks = chunks_result.scalar() or 0
    
    # 文件大小
    size_result = await db.execute(
        select(func.sum(Document.file_size)).where(Document.tenant_id == tenant_id)
    )
    total_file_size = size_result.scalar() or 0
    
    # 状态分布
    status_result = await db.execute(
        select(Document.status, func.count(Document.id))
        .where(Document.tenant_id == tenant_id)
        .group_by(Document.status)
    )
    status_counts = {row[0]: row[1] for row in status_result.all()}
    
    return DocumentStatsResponse(
        document_count=document_count,
        total_chunks=total_chunks,
        total_file_size=total_file_size,
        status_counts=status_counts,
    )
