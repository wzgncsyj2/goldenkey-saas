"""
认证路由
========
用户注册、登录、获取当前用户信息。
"""

from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import CurrentUser, DBSession
from app.core.exceptions import AuthenticationError, ValidationError, NotFoundError
from app.core.config import settings
from app.models.tenant import Tenant, TenantPlan, TenantStatus
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    RegisterResponse,
    TenantResponse,
)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: DBSession,
):
    """
    用户注册
    
    同时创建企业(Tenant)和管理员用户(User)
    """
    # 检查 slug 是否已存在
    existing_slug = await db.execute(
        select(Tenant).where(Tenant.slug == request.tenant_slug)
    )
    if existing_slug.scalar_one_or_none():
        raise ValidationError("租户标识符已被使用")
    
    # 检查用户名是否已存在
    existing_username = await db.execute(
        select(User).where(User.username == request.username)
    )
    if existing_username.scalar_one_or_none():
        raise ValidationError("用户名已被使用")
    
    # 检查邮箱是否已存在
    existing_email = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing_email.scalar_one_or_none():
        raise ValidationError("邮箱已被注册")
    
    # 创建租户
    tenant = Tenant(
        name=request.tenant_name,
        slug=request.tenant_slug,
        plan=TenantPlan.FREE,
        status=TenantStatus.TRIAL,
        max_documents=settings.FREE_MAX_DOCUMENTS,
        max_storage_mb=settings.FREE_MAX_STORAGE_MB,
        max_api_calls_per_day=settings.FREE_MAX_API_CALLS_PER_DAY,
        trial_ends_at=datetime.utcnow(),  # TODO: 加14天
    )
    db.add(tenant)
    await db.flush()
    
    # 创建管理员用户
    user = User(
        tenant_id=tenant.id,
        username=request.username,
        email=request.email,
        display_name=request.username,
        hashed_password=hash_password(request.password),
        role=UserRole.TENANT_ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(tenant)
    
    # 生成 token
    access_token = create_access_token(user.id, tenant.id)
    
    return RegisterResponse(
        user=UserResponse.model_validate(user),
        tenant=TenantResponse.model_validate(tenant),
        access_token=access_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: DBSession,
):
    """
    用户登录
    
    支持用户名或邮箱登录
    """
    # 查找用户（支持用户名或邮箱）
    result = await db.execute(
        select(User).where(
            (User.username == request.username) | (User.email == request.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationError("用户名或密码错误")
    
    if not user.is_active:
        raise AuthenticationError("账号已被禁用")
    
    if not verify_password(request.password, user.hashed_password):
        raise AuthenticationError("用户名或密码错误")
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 生成 token
    access_token = create_access_token(user.id, user.tenant_id)
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
    db: DBSession,
):
    """获取当前登录用户信息"""
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("用户", current_user["user_id"])
    
    return UserResponse.model_validate(user)
