"""
角色相关模式定义
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# 基础模式
class RoleBase(BaseModel):
    """角色基础模式"""
    name: str = Field(..., min_length=2, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    is_default: bool = Field(False, description="是否为默认角色")
    weight: int = Field(100, ge=0, le=1000, description="权重（用于排序）")


class RoleCreate(RoleBase):
    """创建角色请求"""
    permission_ids: List[UUID] = Field(default_factory=list, description="权限ID列表")


class RoleUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    is_default: Optional[bool] = Field(None, description="是否为默认角色")
    weight: Optional[int] = Field(None, ge=0, le=1000, description="权重")


# 响应模式
class RoleSimple(BaseModel):
    """简单角色信息（用于嵌套）"""
    id: UUID
    name: str
    description: Optional[str]
    is_default: bool

    class Config:
        from_attributes = True


class Role(RoleSimple):
    """完整角色信息"""
    weight: int
    created_at: datetime
    updated_at: datetime
    permission_count: int = 0


class RoleDetail(Role):
    """角色详细信息（包含权限）"""
    permissions: List["PermissionSimple"] = []


class RoleListResponse(BaseModel):
    """角色列表响应"""
    data: List[Role]
    meta: dict
    links: dict


# 用户角色关联
class UserRoleAssignment(BaseModel):
    """用户角色分配"""
    user_id: UUID
    role_id: UUID
    assigned_at: datetime
    assigned_by: Optional[UUID]
    expires_at: Optional[datetime]


class AssignRoleRequest(BaseModel):
    """分配角色请求"""
    role_id: UUID = Field(..., description="角色ID")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class AssignRoleResponse(BaseModel):
    """分配角色响应"""
    user_id: UUID
    role_id: UUID
    assigned_at: datetime
    expires_at: Optional[datetime]


# 角色权限关联
class RolePermissionAssignment(BaseModel):
    """角色权限分配"""
    role_id: UUID
    permission_id: UUID
    granted_at: datetime
    granted_by: Optional[UUID]


class AssignPermissionRequest(BaseModel):
    """分配权限请求"""
    permission_id: UUID = Field(..., description="权限ID")


class AssignPermissionResponse(BaseModel):
    """分配权限响应"""
    role_id: UUID
    permission_id: UUID
    granted_at: datetime


# 需要导入PermissionSimple以避免循环导入
from app.schemas.permission import PermissionSimple  # noqa

# 更新前向引用
RoleDetail.update_forward_refs()