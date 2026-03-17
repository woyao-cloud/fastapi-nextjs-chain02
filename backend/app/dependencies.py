"""
依赖注入定义
FastAPI 依赖注入系统的核心定义
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import get_current_user, get_current_active_user
from app.core.permissions import check_permission
from app.exceptions import (
    AuthenticationException,
    AuthorizationException,
    InvalidTokenException,
    TokenExpiredException,
)
from app.infrastructure.database.session import AsyncSessionLocal
from app.schemas.auth import TokenData, UserInDB
from app.schemas.user import User

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    每个请求一个会话，请求结束后自动关闭
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_token_data(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[TokenData]:
    """
    从请求头中提取并验证令牌数据
    如果令牌无效或过期，返回None
    """
    if credentials is None:
        return None

    try:
        from app.core.security import decode_access_token

        token_data = decode_access_token(credentials.credentials)
        return token_data
    except (TokenExpiredException, InvalidTokenException):
        return None
    except Exception:
        # 其他异常也返回None
        return None


async def get_current_user_optional(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserInDB]:
    """
    获取当前用户（可选）
    如果用户未认证，返回None而不是抛出异常
    """
    if token_data is None:
        return None

    try:
        user = await get_current_user(db, token_data.user_id)
        return user
    except Exception:
        return None


async def get_current_user_required(
    current_user: Optional[UserInDB] = Depends(get_current_user_optional),
) -> UserInDB:
    """
    获取当前用户（必需）
    如果用户未认证，抛出认证异常
    """
    if current_user is None:
        raise AuthenticationException(message="认证失败，请先登录")

    return current_user


async def get_current_active_user_required(
    current_user: UserInDB = Depends(get_current_user_required),
) -> UserInDB:
    """
    获取当前活跃用户（必需）
    如果用户账户未激活，抛出异常
    """
    return await get_current_active_user(current_user)


async def get_current_superuser(
    current_user: UserInDB = Depends(get_current_active_user_required),
) -> UserInDB:
    """
    获取当前超级用户
    如果用户不是超级用户，抛出权限异常
    """
    if not current_user.is_superuser:
        raise AuthorizationException(message="需要超级用户权限")

    return current_user


async def require_permission(
    permission: str,
    current_user: UserInDB = Depends(get_current_active_user_required),
) -> UserInDB:
    """
    检查用户是否具有指定权限
    如果没有权限，抛出权限异常
    """
    from app.core.permissions import has_permission

    if not await has_permission(current_user, permission):
        raise AuthorizationException(
            message="权限不足",
            details=f"需要权限: {permission}",
        )

    return current_user


async def rate_limit_dependency(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_current_user_optional),
) -> None:
    """
    速率限制依赖
    根据用户身份和应用限制策略
    """
    from app.core.rate_limit import check_rate_limit

    # 获取用户ID（如果已认证）
    user_id = str(current_user.id) if current_user else None

    # 检查速率限制
    await check_rate_limit(request, user_id)


async def get_request_id(request: Request) -> str:
    """
    获取请求ID依赖
    从请求状态中获取请求ID
    """
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    else:
        # 如果中间件没有设置请求ID，生成一个简单的
        import time
        return f"req_{int(time.time())}"


# 常用权限检查的快捷依赖
require_users_list = Depends(lambda: require_permission("users.list"))
require_users_create = Depends(lambda: require_permission("users.create"))
require_users_read = Depends(lambda: require_permission("users.read"))
require_users_update = Depends(lambda: require_permission("users.update"))
require_users_delete = Depends(lambda: require_permission("users.delete"))

require_roles_list = Depends(lambda: require_permission("roles.list"))
require_roles_create = Depends(lambda: require_permission("roles.create"))
require_roles_read = Depends(lambda: require_permission("roles.read"))
require_roles_update = Depends(lambda: require_permission("roles.update"))
require_roles_delete = Depends(lambda: require_permission("roles.delete"))

require_permissions_list = Depends(lambda: require_permission("permissions.list"))
require_permissions_create = Depends(lambda: require_permission("permissions.create"))
require_permissions_read = Depends(lambda: require_permission("permissions.read"))
require_permissions_update = Depends(lambda: require_permission("permissions.update"))
require_permissions_delete = Depends(lambda: require_permission("permissions.delete"))

require_audit_logs_list = Depends(lambda: require_permission("audit_logs.list"))
require_audit_logs_read = Depends(lambda: require_permission("audit_logs.read"))