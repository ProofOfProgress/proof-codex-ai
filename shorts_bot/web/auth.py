"""Optional bearer token for mutating web API routes."""

from __future__ import annotations

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from shorts_bot.config import settings

_PUBLIC_API_PREFIXES = (
    "/health",
    "/api/status",
    "/api/checklist",
    "/api/login-status",
    "/api/youtube/status",
)


def _extract_token(request: Request) -> str | None:
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    header = request.headers.get("x-api-token")
    return header.strip() if header else None


def require_api_token(request: Request) -> None:
    """FastAPI dependency — raises 401 when WEB_API_TOKEN is set and missing/wrong."""
    expected = (settings.web_api_token or "").strip()
    if not expected:
        return
    got = _extract_token(request)
    if got != expected:
        raise HTTPException(401, "Invalid or missing API token")


class ApiTokenMiddleware(BaseHTTPMiddleware):
    """Block mutating /api/* when WEB_API_TOKEN is configured."""

    async def dispatch(self, request: Request, call_next):
        expected = (settings.web_api_token or "").strip()
        if expected and request.url.path.startswith("/api/"):
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                if not any(request.url.path.startswith(p) for p in _PUBLIC_API_PREFIXES):
                    if _extract_token(request) != expected:
                        return JSONResponse(
                            status_code=401,
                            content={"detail": "Invalid or missing API token"},
                        )
        return await call_next(request)
