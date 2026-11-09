"""
文档相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class DocumentUpdateRequest(BaseModel):
    """更新文档信息"""
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)
    document_id: Optional[int] = None


# ============================================================
# 响应模型
# ============================================================

class DocumentResponse(BaseModel):
    """文档信息响应"""
    id: int
    tenant_id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    tags: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class DocumentProcessResponse(BaseModel):
    """文档处理响应"""
    document_id: int
    filename: str
    text_length: int
    chunk_count: int
    embedding_dim: int
    sample_chunks: List[str]


class SearchResultItem(BaseModel):
    """搜索结果项"""
    chunk_id: str
    text: str
    score: float
    document_id: int
    filename: str
    chunk_index: int


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    result_count: int
    results: List[SearchResultItem]


class DocumentStatsResponse(BaseModel):
    """文档统计响应"""
    document_count: int
    total_chunks: int
    total_file_size: int
    status_counts: dict
