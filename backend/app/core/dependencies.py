"""
依赖注入模块
============
FastAPI 的依赖项，用于认证、租户隔离等。
"""

from typing import Annotated
from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.database import get_db


# ============================================================
# 认证依赖
# ============================================================

async def get_current_user(
    authorization: Annotated[str, Header()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    从 Authorization header 解析当前用户
    
    Header 格式: Bearer <token>
    
    Returns:
        {"user_id": int, "tenant_id": int}
    """
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("无效的认证头格式")
    
    token = authorization[7:]
    payload = decode_access_token(token)
    
    # TODO: 从数据库查询用户，验证用户状态
    # user = await db.get(User, payload["user_id"])
    # if not user or not user.is_active:
    #     raise AuthenticationError("用户不存在或已禁用")
    
    return payload


async def get_current_admin_user(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    验证当前用户是否为租户管理员
    
    TODO: 从数据库查询用户角色
    """
    # user = await db.get(User, current_user["user_id"])
    # if not user.is_admin:
    #     raise AuthorizationError("需要管理员权限")
    
    return current_user


# ============================================================
# 租户依赖
# ============================================================

async def get_tenant_id(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> int:
    """获取当前用户的租户ID"""
    return current_user["tenant_id"]


# ============================================================
# 类型别名（方便使用）
# ============================================================

CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentAdmin = Annotated[dict, Depends(get_current_admin_user)]
TenantID = Annotated[int, Depends(get_tenant_id)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
