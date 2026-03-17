"""
权限核心模块
基于角色的访问控制（RBAC）权限检查
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthorizationException
from app.schemas.user import UserInDB


async def has_permission(user: UserInDB, permission_name: str) -> bool:
    """
    检查用户是否具有指定权限
    """
    # 超级用户拥有所有权限
    if user.is_superuser:
        return True

    # 检查用户权限列表
    return permission_name in user.permissions


async def check_permission(user: UserInDB, permission_name: str) -> None:
    """
    检查用户权限，如果没有则抛出异常
    """
    if not await has_permission(user, permission_name):
        raise AuthorizationException(
            message="权限不足",
            details=f"需要权限: {permission_name}",
        )


async def get_user_permissions(db: AsyncSession, user_id: UUID) -> List[str]:
    """
    获取用户的所有权限
    包括通过角色继承的权限
    """
    from app.infrastructure.database.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)
    return await user_repo.get_user_permissions(user_id)


async def can_access_resource(
    user: UserInDB,
    resource: str,
    action: str,
    resource_owner_id: Optional[UUID] = None,
) -> bool:
    """
    检查用户是否可以访问特定资源
    支持所有权检查（用户只能访问自己的资源）
    """
    # 构建权限名称
    permission_name = f"{resource}.{action}"

    # 检查全局权限
    if await has_permission(user, permission_name):
        return True

    # 检查所有权（如果提供了资源所有者ID）
    if resource_owner_id and str(user.id) == str(resource_owner_id):
        # 用户尝试访问自己的资源
        # 检查是否有对应的 "own" 权限
        own_permission = f"{resource}.own_{action}"
        if await has_permission(user, own_permission):
            return True

    return False


async def check_resource_access(
    user: UserInDB,
    resource: str,
    action: str,
    resource_owner_id: Optional[UUID] = None,
) -> None:
    """
    检查资源访问权限，如果没有则抛出异常
    """
    if not await can_access_resource(user, resource, action, resource_owner_id):
        raise AuthorizationException(
            message="权限不足",
            details=f"无法{action}{resource}"
            + (f"（不属于你）" if resource_owner_id else ""),
        )


# 常用权限检查的快捷函数
async def can_list_users(user: UserInDB) -> bool:
    """检查是否可以列出用户"""
    return await has_permission(user, "users.list")


async def can_create_users(user: UserInDB) -> bool:
    """检查是否可以创建用户"""
    return await has_permission(user, "users.create")


async def can_read_user(user: UserInDB, target_user_id: Optional[UUID] = None) -> bool:
    """检查是否可以读取用户信息"""
    return await can_access_resource(user, "users", "read", target_user_id)


async def can_update_user(user: UserInDB, target_user_id: Optional[UUID] = None) -> bool:
    """检查是否可以更新用户"""
    return await can_access_resource(user, "users", "update", target_user_id)


async def can_delete_user(user: UserInDB, target_user_id: Optional[UUID] = None) -> bool:
    """检查是否可以删除用户"""
    return await can_access_resource(user, "users", "delete", target_user_id)


async def can_manage_user_roles(user: UserInDB) -> bool:
    """检查是否可以管理用户角色"""
    return await has_permission(user, "users.manage_roles")


async def can_manage_user_sessions(user: UserInDB, target_user_id: Optional[UUID] = None) -> bool:
    """检查是否可以管理用户会话"""
    return await can_access_resource(user, "users", "manage_sessions", target_user_id)


async def can_list_roles(user: UserInDB) -> bool:
    """检查是否可以列出角色"""
    return await has_permission(user, "roles.list")


async def can_create_roles(user: UserInDB) -> bool:
    """检查是否可以创建角色"""
    return await has_permission(user, "roles.create")


async def can_read_role(user: UserInDB) -> bool:
    """检查是否可以读取角色信息"""
    return await has_permission(user, "roles.read")


async def can_update_role(user: UserInDB) -> bool:
    """检查是否可以更新角色"""
    return await has_permission(user, "roles.update")


async def can_delete_role(user: UserInDB) -> bool:
    """检查是否可以删除角色"""
    return await has_permission(user, "roles.delete")


async def can_manage_role_permissions(user: UserInDB) -> bool:
    """检查是否可以管理角色权限"""
    return await has_permission(user, "roles.manage_permissions")


async def can_list_permissions(user: UserInDB) -> bool:
    """检查是否可以列出权限"""
    return await has_permission(user, "permissions.list")


async def can_create_permissions(user: UserInDB) -> bool:
    """检查是否可以创建权限"""
    return await has_permission(user, "permissions.create")


async def can_read_permission(user: UserInDB) -> bool:
    """检查是否可以读取权限信息"""
    return await has_permission(user, "permissions.read")


async def can_update_permission(user: UserInDB) -> bool:
    """检查是否可以更新权限"""
    return await has_permission(user, "permissions.update")


async def can_delete_permission(user: UserInDB) -> bool:
    """检查是否可以删除权限"""
    return await has_permission(user, "permissions.delete")


async def can_list_audit_logs(user: UserInDB) -> bool:
    """检查是否可以列出审计日志"""
    return await has_permission(user, "audit_logs.list")


async def can_read_audit_log(user: UserInDB) -> bool:
    """检查是否可以读取审计日志"""
    return await has_permission(user, "audit_logs.read")


# 权限验证装饰器（用于路由处理函数）
def require_permission(permission_name: str):
    """
    权限验证装饰器
    用于路由处理函数，检查用户是否具有指定权限
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取当前用户
            current_user = kwargs.get("current_user")
            if not current_user:
                raise AuthorizationException(message="需要认证")

            # 检查权限
            await check_permission(current_user, permission_name)

            # 执行原函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_resource_access(resource: str, action: str, owner_id_param: str = "user_id"):
    """
    资源访问验证装饰器
    检查用户是否可以访问特定资源（支持所有权检查）
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取当前用户和目标资源所有者ID
            current_user = kwargs.get("current_user")
            if not current_user:
                raise AuthorizationException(message="需要认证")

            resource_owner_id = kwargs.get(owner_id_param)

            # 检查资源访问权限
            await check_resource_access(current_user, resource, action, resource_owner_id)

            # 执行原函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator