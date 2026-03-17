"""
安全核心模块
处理密码哈希、JWT令牌生成和验证等安全相关功能
"""

import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from uuid import UUID

import jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
)
from app.schemas.auth import TokenData, TokenPair

# 密码上下文配置
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)

# JWT 配置
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    """
    return pwd_context.hash(password)


def create_access_token(
    user_id: UUID,
    username: str,
    email: str,
    is_superuser: bool = False,
    permissions: Optional[list] = None,
    additional_claims: Optional[Dict] = None,
) -> str:
    """
    创建访问令牌
    """
    if permissions is None:
        permissions = []

    # 令牌过期时间
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 令牌载荷
    payload = {
        "sub": str(user_id),
        "username": username,
        "email": email,
        "is_superuser": is_superuser,
        "permissions": permissions,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    # 添加额外声明
    if additional_claims:
        payload.update(additional_claims)

    # 生成JWT令牌
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(
    user_id: UUID,
    session_id: Optional[UUID] = None,
    additional_claims: Optional[Dict] = None,
) -> str:
    """
    创建刷新令牌
    """
    # 令牌过期时间
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # 令牌载荷
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    # 添加会话ID（如果提供）
    if session_id:
        payload["session_id"] = str(session_id)

    # 添加额外声明
    if additional_claims:
        payload.update(additional_claims)

    # 生成JWT令牌
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_token_pair(
    user_id: UUID,
    username: str,
    email: str,
    is_superuser: bool = False,
    permissions: Optional[list] = None,
    session_id: Optional[UUID] = None,
) -> TokenPair:
    """
    创建令牌对（访问令牌 + 刷新令牌）
    """
    access_token = create_access_token(
        user_id=user_id,
        username=username,
        email=email,
        is_superuser=is_superuser,
        permissions=permissions,
    )

    refresh_token = create_refresh_token(
        user_id=user_id,
        session_id=session_id,
    )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
    )


def decode_token(token: str) -> Dict:
    """
    解码JWT令牌
    如果令牌无效或过期，抛出相应的异常
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
    except Exception as e:
        # 捕获其他异常并转换为InvalidTokenException
        raise InvalidTokenException()


def decode_access_token(token: str) -> TokenData:
    """
    解码访问令牌并返回TokenData对象
    """
    payload = decode_token(token)

    # 验证令牌类型
    if payload.get("type") != "access":
        raise InvalidTokenException(details="令牌类型错误，应为访问令牌")

    # 提取用户信息
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException(details="令牌中缺少用户ID")

    # 创建TokenData对象
    token_data = TokenData(
        user_id=UUID(user_id),
        username=payload.get("username", ""),
        email=payload.get("email", ""),
        is_superuser=payload.get("is_superuser", False),
        permissions=payload.get("permissions", []),
        token_type=payload.get("type", "access"),
        exp=payload.get("exp"),
        iat=payload.get("iat"),
    )

    return token_data


def decode_refresh_token(token: str) -> Tuple[UUID, Optional[UUID]]:
    """
    解码刷新令牌并返回用户ID和会话ID
    """
    payload = decode_token(token)

    # 验证令牌类型
    if payload.get("type") != "refresh":
        raise InvalidTokenException(details="令牌类型错误，应为刷新令牌")

    # 提取用户ID
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException(details="令牌中缺少用户ID")

    # 提取会话ID（可选）
    session_id_str = payload.get("session_id")
    session_id = UUID(session_id_str) if session_id_str else None

    return UUID(user_id), session_id


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    验证密码强度
    返回 (是否有效, 错误消息)
    """
    # 检查最小长度
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"密码必须至少 {settings.PASSWORD_MIN_LENGTH} 个字符"

    # 检查是否包含数字
    if not any(char.isdigit() for char in password):
        return False, "密码必须包含至少一个数字"

    # 检查是否包含大写字母
    if not any(char.isupper() for char in password):
        return False, "密码必须包含至少一个大写字母"

    # 检查是否包含小写字母
    if not any(char.islower() for char in password):
        return False, "密码必须包含至少一个小写字母"

    # 检查是否包含特殊字符
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False, "密码必须包含至少一个特殊字符 (!@#$%^&*()_+-=[]{}|;:,.<>?)"

    return True, "密码强度符合要求"


def generate_reset_token() -> str:
    """
    生成密码重置令牌
    使用时间戳和随机数的哈希
    """
    import secrets
    import time

    # 生成随机字符串
    random_str = secrets.token_urlsafe(32)

    # 添加时间戳
    timestamp = str(int(time.time()))

    # 组合并哈希
    combined = f"{random_str}:{timestamp}"
    token_hash = hashlib.sha256(combined.encode()).hexdigest()

    return token_hash


def generate_email_verification_token() -> str:
    """
    生成邮箱验证令牌
    """
    import secrets

    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """
    哈希令牌（用于安全存储）
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """
    验证令牌哈希
    """
    return hash_token(token) == token_hash


def check_password_against_history(
    new_password: str,
    password_history: list[str],
    max_history: int = 5,
) -> bool:
    """
    检查新密码是否与历史密码重复
    返回True表示安全（不在历史中），False表示不安全
    """
    for old_password_hash in password_history[-max_history:]:
        if verify_password(new_password, old_password_hash):
            return False
    return True