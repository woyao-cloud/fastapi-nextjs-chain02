"""
认证相关模式定义
登录、注册、令牌等数据验证模式
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from app.config import settings


# 基础模式
class Token(BaseModel):
    """令牌基础模式"""
    access_token: str
    token_type: str = "bearer"


class TokenPair(Token):
    """令牌对模式（访问令牌 + 刷新令牌）"""
    refresh_token: str
    expires_in: int  # 过期时间（秒）


class TokenData(BaseModel):
    """令牌数据模式"""
    user_id: UUID
    username: str
    email: str
    is_superuser: bool = False
    permissions: List[str] = []
    token_type: str = "access"
    exp: Optional[int] = None
    iat: Optional[int] = None


# 登录相关
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH, description="密码")
    remember_me: bool = Field(False, description="记住我")

    @validator("username")
    def validate_username(cls, v):
        import re
        if not re.match(r"^[a-zA-Z0-9_.-]{3,50}$", v):
            raise ValueError("用户名只能包含字母、数字、点、下划线和连字符，长度3-50")
        return v


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserAuthInfo"


# 注册相关
class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH, description="密码")
    first_name: Optional[str] = Field(None, max_length=100, description="名")
    last_name: Optional[str] = Field(None, max_length=100, description="姓")
    phone_number: Optional[str] = Field(None, max_length=20, description="电话号码")

    @validator("username")
    def validate_username(cls, v):
        import re
        if not re.match(r"^[a-zA-Z0-9_.-]{3,50}$", v):
            raise ValueError("用户名只能包含字母、数字、点、下划线和连字符，长度3-50")
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        from app.core.security import validate_password_strength

        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if v is None:
            return v

        import re
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("电话号码格式不正确")
        return v


class RegisterResponse(BaseModel):
    """注册响应"""
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime


# 令牌刷新相关
class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class RefreshTokenResponse(BaseModel):
    """刷新令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# 密码重置相关
class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr = Field(..., description="邮箱")


class ForgotPasswordResponse(BaseModel):
    """忘记密码响应"""
    message: str = "如果邮箱存在，重置链接已发送"


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH, description="新密码")

    @validator("new_password")
    def validate_password_strength(cls, v):
        from app.core.security import validate_password_strength

        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class ResetPasswordResponse(BaseModel):
    """重置密码响应"""
    message: str = "密码重置成功"


# 邮箱验证相关
class VerifyEmailRequest(BaseModel):
    """验证邮箱请求"""
    token: str = Field(..., description="验证令牌")


class VerifyEmailResponse(BaseModel):
    """验证邮箱响应"""
    verified: bool
    message: str = "邮箱验证成功"


# 用户认证信息（用于登录响应）
class UserAuthInfo(BaseModel):
    """用户认证信息"""
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


# 登出相关
class LogoutResponse(BaseModel):
    """登出响应"""
    message: str = "登出成功"


# 当前用户信息
class CurrentUserResponse(BaseModel):
    """当前用户信息响应"""
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar_url: Optional[str]
    phone_number: Optional[str]
    timezone: str = "UTC"
    locale: str = "en-US"
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login_at: Optional[datetime]
    failed_login_attempts: int = 0
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    roles: List["RoleSimple"] = []
    permissions: List[str] = []


# 需要导入RoleSimple以避免循环导入
from app.schemas.role import RoleSimple  # noqa

# 更新前向引用
LoginResponse.update_forward_refs()
CurrentUserResponse.update_forward_refs()