"""
请求追踪中间件
为每个请求生成唯一ID，便于日志追踪和调试
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class TracingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求，添加追踪信息"""
        # 生成或获取请求ID
        request_id = self._get_or_create_request_id(request)

        # 记录请求开始时间
        start_time = time.time()

        # 将请求ID和开始时间存储到request.state
        request.state.request_id = request_id
        request.state.start_time = start_time

        # 处理请求
        response = await call_next(request)

        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id

        # 计算处理时间并添加到响应头
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # 记录请求日志
        self._log_request(request, response, process_time)

        return response

    def _get_or_create_request_id(self, request: Request) -> str:
        """从请求头获取或生成请求ID"""
        # 检查请求头中是否有X-Request-ID
        request_id_header = request.headers.get("X-Request-ID")

        if request_id_header:
            # 使用客户端提供的请求ID
            return request_id_header
        else:
            # 生成新的请求ID
            return f"req_{uuid.uuid4().hex[:16]}"

    def _log_request(self, request: Request, response: Response, process_time: float) -> None:
        """记录请求日志"""
        log_data = {
            "request_id": request.state.request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "timestamp": time.time(),
        }

        # 记录认证信息（如果存在）
        if hasattr(request.state, "user_id"):
            log_data["user_id"] = request.state.user_id

        # 在实际应用中，这里应该使用结构化的日志库（如structlog）
        # 这里为了简单起见，使用print输出
        if request.url.path not in ["/", "/api/v1/health"]:
            print(f"Request log: {log_data}")

        # 对于慢请求进行特殊记录
        if process_time > 1.0:  # 超过1秒的请求
            print(f"Slow request detected: {log_data}")

        # 对于错误响应进行特殊记录
        if response.status_code >= 400:
            print(f"Error response: {log_data}")