"""
认证相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# 请求模型
# ============================================================

class RegisterRequest(BaseModel):
    """注册请求"""
    tenant_name: str = Field(..., min_length=2, max_length=100, description="企业名称")
    tenant_slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$", description="租户标识符")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


# ============================================================
# 响应模型
# ============================================================

class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    tenant_id: int
    username: str
    email: str
    display_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class TenantResponse(BaseModel):
    """租户信息响应"""
    id: int
    name: str
    slug: str
    plan: str
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    """注册响应"""
    user: UserResponse
    tenant: TenantResponse
    access_token: str
    token_type: str = "bearer"
