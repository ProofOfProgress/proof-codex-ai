"""TikTok Shop factory — minimal API (no horror/YouTube UI)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from shorts_bot.__version__ import __version__
from shorts_bot.config import settings
from shorts_bot.web.auth import ApiTokenMiddleware
from shorts_bot.web.deps import get_memory, get_proposer, get_reward_engine

app = FastAPI(title="TikTok Shop Factory", version=__version__)
app.add_middleware(ApiTokenMiddleware)


class ScoreRequest(BaseModel):
    video_label: str
    video_id: str | None = None
    viewed_vs_swiped_away: float | None = None
    retention_rate: float | None = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    swipe_source: str = "manual"
    retention_source: str = "manual"


class FeedbackRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    decision: str = Field(..., pattern="^(approved|rejected)$")


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


@app.post("/api/score")
def score_video(body: ScoreRequest) -> dict:
    """Score clip metrics → reward/punish → optional improvement proposal."""
    from shorts_bot.learning.reflect import reflect_after_sync
    from shorts_bot.learning.score_helpers import propose_reward_improvement
    from shorts_bot.web.deps import get_agent_memory

    metrics = {
        k: v
        for k, v in body.model_dump().items()
        if k != "video_label" and v is not None
    }
    metrics.setdefault("metrics_source", "score_api")
    engine = get_reward_engine()
    result = engine.score(body.video_label, metrics)
    improvement = None
    imp = propose_reward_improvement(get_memory(), get_proposer(), result)
    if imp:
        improvement = {"id": imp.id, "title": imp.title, "pros": imp.pros, "cons": imp.cons}
    reflect_summary = None
    if settings.self_training_enabled:
        reflect = reflect_after_sync(get_memory(), [result], agent_memory_store=get_agent_memory())
        reflect_summary = reflect.summary()
    return {
        "score": result.score,
        "verdict": result.verdict,
        "reason": result.reason,
        "diagnosis": result.diagnosis,
        "breakdown": result.breakdown,
        "improvement": improvement,
        "reflect": reflect_summary,
    }


@app.post("/api/feedback")
def clip_feedback(body: FeedbackRequest) -> dict:
    """Record approve/reject feedback on a clip concept — feeds avoid/repeat rules."""
    from shorts_bot.learning.feedback import learn_from_draft

    msg = learn_from_draft(get_memory(), body.topic, body.reason, body.decision)
    return {"ok": True, "message": msg}


@app.get("/api/learning/status")
def learning_status() -> dict:
    memory = get_memory()
    pending = memory.list_improvements(status="pending", limit=20)
    return {
        "self_training_enabled": settings.self_training_enabled,
        "pending_improvements": len(pending),
        "recent_rewards": memory.recent_rewards(limit=5),
    }


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
<li><a href="/api/learning/status">/api/learning/status</a></li>
</ul>
<p>Self-learning: POST <code>/api/score</code> with clip metrics from TikTok analytics.</p>
<p>CLI: <code>python3 -m shorts_bot.tiktok_shop status</code></p>
<p>Score CLI: <code>python3 -m shorts_bot.learning.score_cli score --label "Product clip" --swipe 65 --retention 40 --views 1200 --reflect</code></p>
</body></html>"""


@app.exception_handler(Exception)
async def unhandled_exception(_request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(exc)})
