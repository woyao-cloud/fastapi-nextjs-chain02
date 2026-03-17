"""
用户相关模式定义
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from app.config import settings


# 基础模式
class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    first_name: Optional[str] = Field(None, max_length=100, description="名")
    last_name: Optional[str] = Field(None, max_length=100, description="姓")
    phone_number: Optional[str] = Field(None, max_length=20, description="电话号码")
    timezone: str = Field("UTC", description="时区")
    locale: str = Field("en-US", description="语言地区")
    is_active: bool = Field(True, description="是否激活")
    is_verified: bool = Field(False, description="是否已验证邮箱")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH, description="密码")
    role_ids: List[UUID] = Field(default_factory=list, description="角色ID列表")

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


class UserUpdate(BaseModel):
    """更新用户请求"""
    first_name: Optional[str] = Field(None, max_length=100, description="名")
    last_name: Optional[str] = Field(None, max_length=100, description="姓")
    phone_number: Optional[str] = Field(None, max_length=20, description="电话号码")
    timezone: Optional[str] = Field(None, description="时区")
    locale: Optional[str] = Field(None, description="语言地区")
    is_active: Optional[bool] = Field(None, description="是否激活")
    avatar_url: Optional[str] = Field(None, description="头像URL")

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if v is None:
            return v

        import re
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("电话号码格式不正确")
        return v


class UserPatch(BaseModel):
    """部分更新用户请求"""
    is_active: Optional[bool] = Field(None, description="是否激活")


# 响应模式
class UserSimple(BaseModel):
    """简单用户信息"""
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class User(UserSimple):
    """完整用户信息"""
    avatar_url: Optional[str]
    phone_number: Optional[str]
    timezone: str
    locale: str
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    roles: List["RoleSimple"] = []


class UserDetail(User):
    """用户详细信息"""
    is_superuser: bool
    failed_login_attempts: int = 0
    locked_until: Optional[datetime]
    deleted_at: Optional[datetime]
    permissions: List[str] = []


class UserInDB(UserDetail):
    """数据库中的用户信息（包含密码哈希）"""
    password_hash: str

    class Config:
        from_attributes = True


# 列表响应
class UserListResponse(BaseModel):
    """用户列表响应"""
    data: List[User]
    meta: dict
    links: dict


# 用户会话相关
class UserSession(BaseModel):
    """用户会话信息"""
    id: UUID
    device_info: dict
    ip_address: str
    last_activity_at: datetime
    created_at: datetime
    expires_at: datetime


class UserSessionListResponse(BaseModel):
    """用户会话列表响应"""
    data: List[UserSession]


# 密码相关
class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH, description="新密码")

    @validator("new_password")
    def validate_password_strength(cls, v):
        from app.core.security import validate_password_strength

        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class ChangePasswordResponse(BaseModel):
    """修改密码响应"""
    message: str = "密码修改成功"


# 用户统计
class UserStats(BaseModel):
    """用户统计信息"""
    total_users: int
    active_users: int
    verified_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int


# 需要导入RoleSimple以避免循环导入
from app.schemas.role import RoleSimple  # noqa

# 更新前向引用
User.update_forward_refs()
UserDetail.update_forward_refs()