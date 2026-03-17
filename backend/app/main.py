"""
FastAPI 应用入口点
用户管理系统后端主应用
"""

import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings
from app.exceptions import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ResourceNotFoundException,
    ValidationException,
)
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.timeout import TimeoutMiddleware
from app.middleware.tracing import TracingMiddleware

# 全局应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="用户管理系统后端 API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# 全局数据库引擎实例
engine: AsyncEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化资源，关闭时清理资源
    """
    global engine

    # 启动时
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Database URL: {settings.DATABASE_URL}")

    # 创建数据库引擎
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG,
    )

    yield

    # 关闭时
    print("Shutting down application...")
    if engine:
        await engine.dispose()


def configure_middleware(app: FastAPI) -> None:
    """配置应用中间件"""

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )

    # 信任主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1", "::1"],
    )

    # GZIP 压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 安全头中间件
    if settings.ENABLE_CSP or settings.ENABLE_HSTS or settings.ENABLE_XSS_PROTECTION:
        app.add_middleware(SecurityHeadersMiddleware)

    # 请求追踪中间件
    app.add_middleware(TracingMiddleware)

    # 超时中间件
    app.add_middleware(TimeoutMiddleware, timeout_seconds=30)


def configure_exception_handlers(app: FastAPI) -> None:
    """配置异常处理器"""

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "validation_error",
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
        )

    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(request: Request, exc: AuthenticationException):
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": "unauthorized",
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(request: Request, exc: AuthorizationException):
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "forbidden",
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
        )

    @app.exception_handler(ResourceNotFoundException)
    async def not_found_exception_handler(request: Request, exc: ResourceNotFoundException):
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "not_found",
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
        )

    @app.exception_handler(BusinessLogicException)
    async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "unprocessable_entity",
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
        )

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # 生产环境下隐藏详细错误信息
        if settings.DEBUG:
            message = str(exc)
            details = {"traceback": exc.__traceback__} if hasattr(exc, "__traceback__") else None
        else:
            message = "服务器内部错误"
            details = None

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": message,
                    "details": details,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
                    "timestamp": time.time(),
                }
            },
        )


def configure_routes(app: FastAPI) -> None:
    """配置应用路由"""

    # 导入路由模块
    from app.api.v1 import auth, health, users, roles, permissions, audit_logs

    # API v1 路由
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1", tags=["users"])
    app.include_router(roles.router, prefix="/api/v1", tags=["roles"])
    app.include_router(permissions.router, prefix="/api/v1", tags=["permissions"])
    app.include_router(audit_logs.router, prefix="/api/v1", tags=["audit_logs"])

    # 根路径健康检查
    @app.get("/")
    async def root():
        return {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "running",
            "timestamp": time.time(),
            "documentation": "/docs" if settings.DEBUG else None,
        }


def configure_openapi(app: FastAPI) -> None:
    """配置 OpenAPI 文档"""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description="用户管理系统后端 API",
            routes=app.routes,
        )

        # 添加安全方案
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT 认证令牌",
            }
        }

        # 为需要认证的端点添加安全要求
        for path, path_item in openapi_schema.get("paths", {}).items():
            for method, operation in path_item.items():
                # 排除健康检查等公开端点
                if path not in ["/", "/api/v1/health", "/api/v1/auth/login", "/api/v1/auth/register"]:
                    operation.setdefault("security", []).append({"BearerAuth": []})

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi


def create_app() -> FastAPI:
    """创建和配置 FastAPI 应用"""

    # 配置中间件
    configure_middleware(app)

    # 配置异常处理器
    configure_exception_handlers(app)

    # 配置路由
    configure_routes(app)

    # 配置 OpenAPI
    configure_openapi(app)

    return app


# 创建应用实例
create_app()