from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from shorts_bot.config import settings
from shorts_bot.web.deps import get_agent, get_memory, get_proposer, get_reward_engine, get_store

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app = FastAPI(title="Shorts Bot", version="0.2.0")
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ChatRequest(BaseModel):
    message: str


class ImprovementDecision(BaseModel):
    note: str = ""


class ScoreRequest(BaseModel):
    video_label: str
    viewed_vs_swiped_away: float | None = None
    retention_rate: float | None = None
    views: int = 0
    likes: int = 0
    comments: int = 0


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    memory = get_memory()
    store = get_store()
    return TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "has_openai": settings.has_openai,
            "channel": store.channel_summary(),
            "improvements": memory.list_improvements(status="pending"),
            "drafts": store.list_drafts(status="pending"),
            "rewards": memory.recent_rewards(limit=5),
        },
    )


@app.post("/api/chat")
async def chat(body: ChatRequest) -> dict:
    if not body.message.strip():
        raise HTTPException(400, "Empty message")
    agent = get_agent()
    reply = agent.chat(body.message.strip())
    return {"reply": reply}


@app.get("/api/improvements")
async def list_improvements() -> dict:
    memory = get_memory()
    pending = memory.list_improvements(status="pending")
    return {
        "pending": [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "description": i.description,
                "pros": i.pros,
                "cons": i.cons,
                "source": i.source,
            }
            for i in pending
        ]
    }


@app.post("/api/improvements/{improvement_id}/yes")
async def approve_improvement(improvement_id: int, body: ImprovementDecision) -> dict:
    memory = get_memory()
    try:
        imp = memory.review_improvement(improvement_id, approved=True, note=body.note or "Approved.")
    except KeyError:
        raise HTTPException(404, "Not found") from None
    return {"status": imp.status, "title": imp.title}


@app.post("/api/improvements/{improvement_id}/no")
async def reject_improvement(improvement_id: int, body: ImprovementDecision) -> dict:
    memory = get_memory()
    try:
        imp = memory.review_improvement(improvement_id, approved=False, note=body.note or "Rejected.")
    except KeyError:
        raise HTTPException(404, "Not found") from None
    return {"status": imp.status, "title": imp.title}


@app.post("/api/drafts/{draft_id}/yes")
async def approve_draft(draft_id: int, body: ImprovementDecision) -> dict:
    store = get_store()
    try:
        d = store.review_draft(draft_id, "approved", body.note or "Approved.")
    except KeyError:
        raise HTTPException(404, "Not found") from None
    get_proposer().propose_from_feedback(d.topic, body.note or "Approved", "approved")
    return {"status": d.status}


@app.post("/api/drafts/{draft_id}/no")
async def reject_draft(draft_id: int, body: ImprovementDecision) -> dict:
    store = get_store()
    if not body.note.strip():
        raise HTTPException(400, "Rejection reason required")
    try:
        d = store.review_draft(draft_id, "rejected", body.note)
    except KeyError:
        raise HTTPException(404, "Not found") from None
    get_proposer().propose_from_feedback(d.topic, body.note, "rejected")
    return {"status": d.status}


@app.post("/api/score")
async def score_video(body: ScoreRequest) -> dict:
    metrics = {
        k: v
        for k, v in body.model_dump().items()
        if k != "video_label" and v is not None
    }
    engine = get_reward_engine()
    result = engine.score(body.video_label, metrics)
    improvement = None
    proposer = get_proposer()
    imp = proposer.propose_from_reward(result)
    if imp:
        improvement = {"id": imp.id, "title": imp.title, "pros": imp.pros, "cons": imp.cons}
    return {
        "score": result.score,
        "verdict": result.verdict,
        "reason": result.reason,
        "diagnosis": result.diagnosis,
        "improvement": improvement,
    }


@app.get("/api/status")
async def status() -> dict:
    store = get_store()
    memory = get_memory()
    return {
        "openai": settings.has_openai,
        "channel": store.channel_summary(),
        "stats": store.stats(),
        "pending_improvements": len(memory.list_improvements(status="pending")),
        "applied_training": memory.applied_improvements(),
    }
