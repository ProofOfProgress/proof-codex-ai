"""Optional bearer token for mutating web API routes."""

from __future__ import annotations

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from shorts_bot.config import settings

_PUBLIC_API_PREFIXES = (
    "/health",
    "/api/status",
    "/api/tiktok-shop/status",
    "/api/printify/status",
    "/api/kling/status",
)


def require_api_token(request: Request) -> None:
    expected = (settings.web_api_token or "").strip()
    if not expected:
        return
    auth = request.headers.get("authorization") or ""
    token = auth[7:].strip() if auth.lower().startswith("bearer ") else (request.headers.get("x-api-token") or "").strip()
    if token != expected:
        raise HTTPException(401, "Invalid or missing API token")


class ApiTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        expected = (settings.web_api_token or "").strip()
        if expected and request.url.path.startswith("/api/") and request.method not in ("GET", "HEAD", "OPTIONS"):
            if not any(request.url.path.startswith(p) for p in _PUBLIC_API_PREFIXES):
                auth = request.headers.get("authorization") or ""
                token = auth[7:].strip() if auth.lower().startswith("bearer ") else (request.headers.get("x-api-token") or "").strip()
                if token != expected:
                    return JSONResponse(status_code=401, content={"detail": "Invalid or missing API token"})
        return await call_next(request)
