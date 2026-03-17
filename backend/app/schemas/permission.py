"""
权限相关模式定义
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# 基础模式
class PermissionBase(BaseModel):
    """权限基础模式"""
    name: str = Field(..., min_length=3, max_length=100, description="权限名称")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")
    resource: str = Field(..., min_length=2, max_length=50, description="资源名称")
    action: str = Field(..., min_length=2, max_length=50, description="操作名称")
    scope: str = Field("global", min_length=2, max_length=50, description="作用范围")


class PermissionCreate(PermissionBase):
    """创建权限请求"""
    pass


class PermissionUpdate(BaseModel):
    """更新权限请求"""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="权限名称")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")
    resource: Optional[str] = Field(None, min_length=2, max_length=50, description="资源名称")
    action: Optional[str] = Field(None, min_length=2, max_length=50, description="操作名称")
    scope: Optional[str] = Field(None, min_length=2, max_length=50, description="作用范围")


# 响应模式
class PermissionSimple(BaseModel):
    """简单权限信息（用于嵌套）"""
    id: UUID
    name: str
    description: Optional[str]
    resource: str
    action: str

    class Config:
        from_attributes = True


class Permission(PermissionSimple):
    """完整权限信息"""
    scope: str
    created_at: datetime
    updated_at: datetime


class PermissionDetail(Permission):
    """权限详细信息"""
    role_count: int = 0


class PermissionListResponse(BaseModel):
    """权限列表响应"""
    data: List[Permission]
    meta: dict
    links: dict


# 权限检查
class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    permission: str = Field(..., description="权限名称")


class PermissionCheckResponse(BaseModel):
    """权限检查响应"""
    has_permission: bool
    user_id: UUID
    permission: str