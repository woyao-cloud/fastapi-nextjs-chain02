"""
自定义异常类
定义 API 业务逻辑中的各种异常
"""

from typing import Any, Dict, List, Optional


class APIException(Exception):
    """API 基础异常类"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = "internal_server_error",
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)


class ValidationException(APIException):
    """输入验证异常"""

    def __init__(
        self,
        message: str = "输入验证失败",
        details: Optional[List[Dict[str, str]]] = None,
    ):
        super().__init__(
            message=message,
            status_code=400,
            code="validation_error",
            details=details,
        )


class AuthenticationException(APIException):
    """认证异常"""

    def __init__(
        self,
        message: str = "认证失败",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            code="unauthorized",
            details=details,
        )


class AuthorizationException(APIException):
    """授权异常"""

    def __init__(
        self,
        message: str = "权限不足",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            code="forbidden",
            details=details,
        )


class ResourceNotFoundException(APIException):
    """资源未找到异常"""

    def __init__(
        self,
        message: str = "资源不存在",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=404,
            code="not_found",
            details=details,
        )


class BusinessLogicException(APIException):
    """业务逻辑异常"""

    def __init__(
        self,
        message: str = "业务逻辑错误",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=422,
            code="unprocessable_entity",
            details=details,
        )


class ConflictException(APIException):
    """资源冲突异常"""

    def __init__(
        self,
        message: str = "资源冲突",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=409,
            code="conflict",
            details=details,
        )


class RateLimitException(APIException):
    """速率限制异常"""

    def __init__(
        self,
        message: str = "请求频率超限",
        details: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(
            message=message,
            status_code=429,
            code="rate_limit_exceeded",
            details=details,
        )
        self.retry_after = retry_after


class ServiceUnavailableException(APIException):
    """服务不可用异常"""

    def __init__(
        self,
        message: str = "服务暂时不可用",
        details: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(
            message=message,
            status_code=503,
            code="service_unavailable",
            details=details,
        )
        self.retry_after = retry_after


class DatabaseException(APIException):
    """数据库异常"""

    def __init__(
        self,
        message: str = "数据库操作失败",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=500,
            code="database_error",
            details=details,
        )


class ExternalServiceException(APIException):
    """外部服务异常"""

    def __init__(
        self,
        message: str = "外部服务调用失败",
        details: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=502,
            code="external_service_error",
            details=details,
        )


# 特定业务异常
class UserAlreadyExistsException(ConflictException):
    """用户已存在异常"""

    def __init__(self, username: str, email: str):
        super().__init__(
            message="用户已存在",
            details=f"用户名 '{username}' 或邮箱 '{email}' 已被注册",
        )


class InvalidCredentialsException(AuthenticationException):
    """无效凭证异常"""

    def __init__(self):
        super().__init__(
            message="用户名或密码错误",
            details="请检查用户名和密码是否正确",
        )


class AccountLockedException(AuthenticationException):
    """账户锁定异常"""

    def __init__(self, locked_until: Optional[str] = None):
        details = "账户已被锁定"
        if locked_until:
            details += f"，锁定至 {locked_until}"
        super().__init__(
            message="账户已被锁定",
            details=details,
        )


class TokenExpiredException(AuthenticationException):
    """令牌过期异常"""

    def __init__(self):
        super().__init__(
            message="访问令牌已过期",
            details="请重新登录或刷新令牌",
        )


class InvalidTokenException(AuthenticationException):
    """无效令牌异常"""

    def __init__(self):
        super().__init__(
            message="无效的访问令牌",
            details="令牌格式不正确或已被撤销",
        )


class InsufficientPermissionsException(AuthorizationException):
    """权限不足异常"""

    def __init__(self, required_permission: str):
        super().__init__(
            message="权限不足",
            details=f"需要权限: {required_permission}",
        )


class UserNotFoundException(ResourceNotFoundException):
    """用户未找到异常"""

    def __init__(self, user_id: str):
        super().__init__(
            message="用户不存在",
            details=f"用户ID: {user_id}",
        )


class RoleNotFoundException(ResourceNotFoundException):
    """角色未找到异常"""

    def __init__(self, role_id: str):
        super().__init__(
            message="角色不存在",
            details=f"角色ID: {role_id}",
        )


class PermissionNotFoundException(ResourceNotFoundException):
    """权限未找到异常"""

    def __init__(self, permission_id: str):
        super().__init__(
            message="权限不存在",
            details=f"权限ID: {permission_id}",
        )