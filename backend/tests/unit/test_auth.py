"""
认证模块单元测试
"""

import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.exceptions import AuthenticationError


class TestPasswordHashing:
    """密码哈希测试"""
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password("wrong_password", hashed) is False


class TestJWT:
    """JWT Token 测试"""
    
    def test_create_and_decode_token(self):
        """测试创建和解码 Token"""
        user_id = 1
        tenant_id = 10
        
        token = create_access_token(user_id, tenant_id)
        payload = decode_access_token(token)
        
        assert payload["user_id"] == user_id
        assert payload["tenant_id"] == tenant_id
    
    def test_decode_invalid_token(self):
        """测试解码无效 Token"""
        with pytest.raises(AuthenticationError):
            decode_access_token("invalid_token")
