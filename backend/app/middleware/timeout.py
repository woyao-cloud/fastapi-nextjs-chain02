"""
请求超时中间件
防止长时间运行的请求占用服务器资源
"""

import asyncio
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.exceptions import ServiceUnavailableException


class TimeoutMiddleware(BaseHTTPMiddleware):
    """超时中间件"""

    def __init__(self, app: ASGIApp, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求，设置超时限制"""
        try:
            # 使用 asyncio.timeout 设置超时
            async with asyncio.timeout(self.timeout_seconds):
                response = await call_next(request)
                return response

        except asyncio.TimeoutError:
            # 记录超时请求
            self._log_timeout(request)

            # 返回超时错误响应
            raise ServiceUnavailableException(
                message="请求处理超时",
                details=f"请求在 {self.timeout_seconds} 秒内未完成",
                retry_after=30,
            )

        except Exception as e:
            # 重新抛出其他异常
            raise e

    def _log_timeout(self, request: Request) -> None:
        """记录超时请求信息"""
        timeout_info = {
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "query_params": dict(request.query_params),
            "timeout_seconds": self.timeout_seconds,
            "timestamp": time.time(),
        }

        # 在实际应用中，这里应该记录到日志系统
        print(f"Request timeout: {timeout_info}")

        # 如果有请求ID，也记录下来
        if hasattr(request.state, "request_id"):
            print(f"Request ID: {request.state.request_id}")