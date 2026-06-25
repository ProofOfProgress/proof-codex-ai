"""TikTok Shop factory — minimal API (no horror/YouTube UI)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from shorts_bot.__version__ import __version__
from shorts_bot.web.auth import ApiTokenMiddleware

app = FastAPI(title="TikTok Shop Factory", version=__version__)
app.add_middleware(ApiTokenMiddleware)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "tiktok-shop-factory"}


@app.get("/api/status")
def api_status() -> dict:
    from shorts_bot.tiktok_shop import echotik_client, kling_client
    from shorts_bot.tiktok_shop import printify_client

    return {
        "version": __version__,
        "echotik": echotik_client.configured(),
        "kling": kling_client.configured(),
        "printify": printify_client.configured(),
    }


@app.get("/api/tiktok-shop/status")
def tiktok_shop_status() -> dict:
    from shorts_bot.tiktok_shop.accounts import load_accounts, total_daily_cap
    from shorts_bot.tiktok_shop.quota import status_rows

    accounts = load_accounts()
    return {
        "accounts": len(accounts),
        "daily_cap": total_daily_cap(),
        "quota": status_rows(),
    }


@app.get("/api/printify/status")
def printify_status() -> dict:
    from shorts_bot.tiktok_shop import printify_client

    if not printify_client.configured():
        return {"configured": False}
    try:
        shops = printify_client.list_shops()
        return {"configured": True, "shops": len(shops), "shop_ids": [s.get("id") for s in shops[:5]]}
    except Exception as exc:
        return {"configured": True, "error": str(exc)}


@app.get("/api/kling/status")
def kling_status() -> dict:
    from shorts_bot.tiktok_shop import kling_client

    return {"configured": kling_client.configured()}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>TikTok Shop Factory</title></head>
<body style="font-family:system-ui;max-width:640px;margin:2rem auto;padding:0 1rem">
<h1>TikTok Shop Factory</h1>
<p>API-only UI. Check status:</p>
<ul>
<li><a href="/api/status">/api/status</a></li>
<li><a href="/api/tiktok-shop/status">/api/tiktok-shop/status</a></li>
<li><a href="/api/printify/status">/api/printify/status</a></li>
</ul>
<p>CLI: <code>python3 -m shorts_bot.tiktok_shop status</code></p>
</body></html>"""


@app.exception_handler(Exception)
async def unhandled_exception(_request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(exc)})
