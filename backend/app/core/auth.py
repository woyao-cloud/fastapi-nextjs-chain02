"""
认证核心模块
用户认证和授权相关逻辑
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    AccountLockedException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.infrastructure.database.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserInDB


async def authenticate_user(
    db: AsyncSession,
    login_data: LoginRequest,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserInDB:
    """
    用户认证
    验证用户名/密码，检查账户状态，记录登录尝试
    """
    from app.infrastructure.database.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)

    # 查找用户（支持用户名或邮箱登录）
    user = await user_repo.get_by_username_or_email(login_data.username)

    if not user:
        # 记录失败的登录尝试
        await _record_failed_login_attempt(
            db, login_data.username, ip_address, user_agent, success=False
        )
        raise InvalidCredentialsException()

    # 检查账户是否被锁定
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise AccountLockedException(locked_until=user.locked_until.isoformat())

    # 验证密码
    from app.core.security import verify_password

    if not verify_password(login_data.password, user.password_hash):
        # 密码错误，增加失败计数
        await _increment_failed_login_attempts(db, user)

        # 记录失败的登录尝试
        await _record_failed_login_attempt(
            db, login_data.username, ip_address, user_agent, success=False, user_id=user.id
        )

        raise InvalidCredentialsException()

    # 检查账户是否激活
    if not user.is_active:
        raise InvalidCredentialsException(details="账户未激活")

    # 登录成功，重置失败计数
    await _reset_failed_login_attempts(db, user)

    # 更新最后登录时间
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    # 记录成功的登录尝试
    await _record_failed_login_attempt(
        db, login_data.username, ip_address, user_agent, success=True, user_id=user.id
    )

    # 创建用户会话（如果需要）
    if login_data.remember_me:
        from app.infrastructure.database.repositories.session_repository import SessionRepository

        session_repo = SessionRepository(db)
        await session_repo.create_session(
            user_id=user.id,
            device_info=_parse_user_agent(user_agent),
            ip_address=ip_address,
            remember_me=True,
        )

    return user


async def get_current_user(db: AsyncSession, user_id: UUID) -> UserInDB:
    """
    获取当前用户
    根据用户ID从数据库获取用户信息
    """
    from app.infrastructure.database.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UserNotFoundException(str(user_id))

    return user


async def get_current_active_user(user: UserInDB) -> UserInDB:
    """
    获取当前活跃用户
    检查用户账户是否激活
    """
    if not user.is_active:
        raise InvalidCredentialsException(details="账户未激活")

    return user


async def logout_user(
    db: AsyncSession,
    user_id: UUID,
    session_id: Optional[UUID] = None,
) -> None:
    """
    用户登出
    终止指定会话或所有会话
    """
    from app.infrastructure.database.repositories.session_repository import SessionRepository

    session_repo = SessionRepository(db)

    if session_id:
        # 终止指定会话
        await session_repo.delete_session(session_id)
    else:
        # 终止用户的所有会话
        await session_repo.delete_user_sessions(user_id)


async def refresh_user_session(
    db: AsyncSession,
    user_id: UUID,
    old_session_id: UUID,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UUID:
    """
    刷新用户会话
    创建新会话，终止旧会话
    """
    from app.infrastructure.database.repositories.session_repository import SessionRepository

    session_repo = SessionRepository(db)

    # 创建新会话
    new_session = await session_repo.create_session(
        user_id=user_id,
        device_info=_parse_user_agent(user_agent),
        ip_address=ip_address,
        remember_me=True,
    )

    # 终止旧会话
    await session_repo.delete_session(old_session_id)

    return new_session.id


async def verify_email_token(db: AsyncSession, token: str) -> UserInDB:
    """
    验证邮箱令牌
    """
    from app.infrastructure.database.repositories.verification_repository import VerificationRepository

    verification_repo = VerificationRepository(db)
    verification = await verification_repo.get_valid_verification_by_token(token)

    if not verification:
        raise InvalidCredentialsException(details="验证令牌无效或已过期")

    # 获取用户
    from app.infrastructure.database.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(verification.user_id)

    if not user:
        raise UserNotFoundException(str(verification.user_id))

    # 标记邮箱为已验证
    user.is_verified = True
    verification.verified_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # 删除验证记录
    await verification_repo.delete(verification.id)

    return user


async def reset_password(
    db: AsyncSession,
    token: str,
    new_password: str,
) -> UserInDB:
    """
    重置密码
    """
    from app.infrastructure.database.repositories.password_reset_repository import PasswordResetRepository
    from app.core.security import get_password_hash

    password_reset_repo = PasswordResetRepository(db)
    reset_request = await password_reset_repo.get_valid_reset_by_token(token)

    if not reset_request:
        raise InvalidCredentialsException(details="重置令牌无效或已过期")

    # 获取用户
    from app.infrastructure.database.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(reset_request.user_id)

    if not user:
        raise UserNotFoundException(str(reset_request.user_id))

    # 更新密码
    user.password_hash = get_password_hash(new_password)
    reset_request.used_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # 删除重置记录
    await password_reset_repo.delete(reset_request.id)

    # 终止用户的所有会话（安全措施）
    from app.infrastructure.database.repositories.session_repository import SessionRepository

    session_repo = SessionRepository(db)
    await session_repo.delete_user_sessions(user.id)

    return user


# 辅助函数
async def _increment_failed_login_attempts(db: AsyncSession, user: User) -> None:
    """增加登录失败计数"""
    from app.config import settings

    user.failed_login_attempts += 1

    # 检查是否达到最大尝试次数
    if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        from datetime import timedelta

        # 锁定账户
        user.locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCOUNT_LOCKOUT_MINUTES
        )

    await db.commit()


async def _reset_failed_login_attempts(db: AsyncSession, user: User) -> None:
    """重置登录失败计数"""
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.locked_until = None
        await db.commit()


async def _record_failed_login_attempt(
    db: AsyncSession,
    username: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    success: bool,
    user_id: Optional[UUID] = None,
) -> None:
    """记录登录尝试"""
    from app.infrastructure.database.repositories.login_attempt_repository import LoginAttemptRepository

    login_attempt_repo = LoginAttemptRepository(db)

    await login_attempt_repo.create(
        username=username,
        ip_address=ip_address or "unknown",
        user_agent=user_agent or "unknown",
        success=success,
        user_id=user_id,
    )


def _parse_user_agent(user_agent: Optional[str]) -> dict:
    """解析User-Agent字符串"""
    if not user_agent:
        return {"browser": "unknown", "os": "unknown", "device": "unknown"}

    # 简化的解析逻辑
    # 在实际应用中，应该使用专门的库如user_agents
    info = {"browser": "unknown", "os": "unknown", "device": "unknown"}

    user_agent_lower = user_agent.lower()

    # 浏览器检测
    if "chrome" in user_agent_lower and "edg" not in user_agent_lower:
        info["browser"] = "Chrome"
    elif "firefox" in user_agent_lower:
        info["browser"] = "Firefox"
    elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
        info["browser"] = "Safari"
    elif "edge" in user_agent_lower:
        info["browser"] = "Edge"
    elif "opera" in user_agent_lower:
        info["browser"] = "Opera"

    # 操作系统检测
    if "windows" in user_agent_lower:
        info["os"] = "Windows"
    elif "mac os" in user_agent_lower:
        info["os"] = "macOS"
    elif "linux" in user_agent_lower:
        info["os"] = "Linux"
    elif "android" in user_agent_lower:
        info["os"] = "Android"
    elif "ios" in user_agent_lower or "iphone" in user_agent_lower:
        info["os"] = "iOS"

    # 设备类型检测
    if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
        info["device"] = "Mobile"
    elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        info["device"] = "Tablet"
    else:
        info["device"] = "Desktop"

    return info