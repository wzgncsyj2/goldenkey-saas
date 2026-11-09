"""
安全模块
========
JWT 认证、密码哈希、权限验证。
"""

from datetime import datetime, timedelta
from typing import Optional, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationError


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# 密码哈希
# ============================================================

def hash_password(password: str) -> str:
    """将明文密码转为哈希值"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希值是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT Token
# ============================================================

def create_access_token(
    user_id: int,
    tenant_id: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建 JWT 访问令牌
    
    Args:
        user_id: 用户ID
        tenant_id: 租户ID
        expires_delta: 过期时间增量
    
    Returns:
        编码后的 JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(user_id),        # JWT标准要求sub是字符串
        "tenant_id": str(tenant_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    解码并验证 JWT token
    
    Args:
        token: JWT token 字符串
    
    Returns:
        解码后的 payload 字典
    
    Raises:
        AuthenticationError: token 无效或已过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        user_id: Optional[str] = payload.get("sub")
        tenant_id: Optional[str] = payload.get("tenant_id")
        
        if user_id is None or tenant_id is None:
            raise AuthenticationError("无效的令牌")
        
        return {
            "user_id": int(user_id),
            "tenant_id": int(tenant_id),
        }
        
    except JWTError as e:
        raise AuthenticationError(f"令牌验证失败: {str(e)}")
