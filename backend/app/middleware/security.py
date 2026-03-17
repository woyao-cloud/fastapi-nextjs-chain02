"""
安全头中间件
设置 CSP、HSTS、XSS 保护等安全头
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = self._build_security_headers()

    def _build_security_headers(self) -> dict:
        """构建安全头字典"""
        headers = {}

        # Content Security Policy
        if settings.ENABLE_CSP:
            csp_policies = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                "connect-src 'self'",
                "media-src 'self'",
                "object-src 'none'",
                "child-src 'self'",
                "frame-ancestors 'self'",
                "form-action 'self'",
                "base-uri 'self'",
                "manifest-src 'self'",
            ]
            headers["Content-Security-Policy"] = "; ".join(csp_policies)

        # HTTP Strict Transport Security
        if settings.ENABLE_HSTS:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # XSS Protection
        if settings.ENABLE_XSS_PROTECTION:
            headers["X-XSS-Protection"] = "1; mode=block"

        # 其他安全头
        headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
                "battery=(), camera=(), cross-origin-isolated=(), "
                "display-capture=(), document-domain=(), encrypted-media=(), "
                "execution-while-not-rendered=(), execution-while-out-of-viewport=(), "
                "fullscreen=(), geolocation=(), gyroscope=(), "
                "keyboard-map=(), magnetometer=(), microphone=(), "
                "midi=(), navigation-override=(), payment=(), picture-in-picture=(), "
                "publickey-credentials-get=(), screen-wake-lock=(), "
                "serial=(), speaker-selection=(), storage-access=(), "
                "sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=()"
            ),
        })

        return headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求，添加安全头"""
        response = await call_next(request)

        # 添加安全头
        for header, value in self.security_headers.items():
            response.headers[header] = value

        # 添加自定义安全头
        response.headers["X-Powered-By"] = f"FastAPI/{settings.PROJECT_NAME}"
        response.headers["Server"] = "SecureServer"

        # 添加请求时间头
        if hasattr(request.state, "start_time"):
            process_time = time.time() - request.state.start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response