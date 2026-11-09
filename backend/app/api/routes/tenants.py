"""
租户路由
========
租户管理、配额查询、品牌配置。
"""

from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import CurrentUser, CurrentAdmin, TenantID, DBSession
from app.core.exceptions import NotFoundError
from app.models.tenant import Tenant
from app.schemas.auth import TenantResponse

router = APIRouter()


@router.get("/me", response_model=TenantResponse)
async def get_current_tenant(
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取当前租户信息"""
    tenant = await db.get(Tenant, tenant_id)
    
    if not tenant:
        raise NotFoundError("租户", tenant_id)
    
    return TenantResponse.model_validate(tenant)


@router.get("/me/quota")
async def get_quota(
    current_user: CurrentUser,
    tenant_id: TenantID,
    db: DBSession,
):
    """获取当前配额使用情况"""
    tenant = await db.get(Tenant, tenant_id)
    
    return {
        "plan": tenant.plan,
        "documents": {
            "used": 0,  # TODO: 查询实际使用量
            "limit": tenant.max_documents,
        },
        "storage_mb": {
            "used": tenant.current_storage_mb,
            "limit": tenant.max_storage_mb,
        },
        "api_calls_today": {
            "used": tenant.api_calls_today,
            "limit": tenant.max_api_calls_per_day,
        },
    }


@router.put("/me/branding")
async def update_branding(
    branding: dict,
    current_admin: CurrentAdmin,
    tenant_id: TenantID,
    db: DBSession,
):
    """更新品牌配置（仅管理员）"""
    tenant = await db.get(Tenant, tenant_id)
    
    tenant.branding = branding
    await db.commit()
    
    return {"message": "品牌配置已更新", "branding": branding}
