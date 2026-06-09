from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from shorts_bot.__version__ import __version__
from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.web.deps import (
    get_agent,
    get_analytics_sync,
    get_memory,
    get_proposer,
    get_reward_engine,
    get_store,
)
from shorts_bot.youtube.google_auth import auth_status

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app = FastAPI(title="Soft Continuity Operator", version="0.7.0")


@app.exception_handler(Exception)
async def unhandled_exception(_request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "message": "Something went wrong — try again."},
    )


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


class DevRequest(BaseModel):
    title: str
    description: str


class ProductionRequest(BaseModel):
    draft_id: int
    turboscribe_text: str = Field(min_length=10)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    memory = get_memory()
    store = get_store()
    learned = LearnedFile(settings.learned_path)
    from shorts_bot.services.ops import BotOperations

    pending_imps = memory.list_improvements(status="pending")
    return TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "has_openai": settings.has_openai,
            "has_discord": settings.has_discord,
            "channel": store.channel_summary(),
            "checklist": BotOperations().setup_checklist(),
            "first_improvement": pending_imps[0] if pending_imps else None,
            "improvements": pending_imps,
            "drafts": store.list_drafts(status="pending"),
            "dev_tasks": memory.list_dev_tasks(status="pending"),
            "rewards": memory.recent_rewards(limit=8),
            "journal": memory.learning_journal(limit=10),
            "learned_preview": learned.read_tail(3500),
            "youtube": auth_status(),
            "pending_count": len(memory.list_improvements(status="pending")),
            "pending_drafts": len(store.list_drafts(status="pending")),
            "pending_dev": len(memory.list_dev_tasks(status="pending")),
            "version": __version__,
        },
    )


@app.get("/health")
async def health() -> dict:
    store = get_store()
    memory = get_memory()
    return {
        "ok": True,
        "version": __version__,
        "openai": settings.has_openai,
        "discord": settings.has_discord,
        "pending_improvements": len(memory.list_improvements(status="pending")),
        "pending_drafts": len(store.list_drafts(status="pending")),
        "pending_dev": len(memory.list_dev_tasks(status="pending")),
        "youtube": auth_status(),
    }


@app.post("/api/chat")
async def chat(body: ChatRequest) -> dict:
    if not body.message.strip():
        raise HTTPException(400, "Empty message")
    if len(body.message) > 8000:
        raise HTTPException(400, "Message too long (max 8000 chars)")
    try:
        from shorts_bot.services.ops import BotOperations

        reply = BotOperations().chat(body.message.strip())
        return {"reply": reply}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"Chat error: {exc}") from exc


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
    LearnedFile(settings.learned_path).record_improvement(imp, approved=True)
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
        "breakdown": result.breakdown,
        "improvement": improvement,
    }


@app.get("/api/checklist")
async def setup_checklist() -> dict:
    from shorts_bot.services.ops import BotOperations

    return {"items": BotOperations().setup_checklist()}


@app.get("/api/status")
async def status() -> dict:
    store = get_store()
    memory = get_memory()
    return {
        "openai": settings.has_openai,
        "channel": store.channel_summary(),
        "stats": store.stats(),
        "pending_improvements": len(memory.list_improvements(status="pending")),
        "pending_drafts": len(store.list_drafts(status="pending")),
        "pending_dev": len(memory.list_dev_tasks(status="pending")),
        "discord": settings.has_discord,
        "applied_training": memory.applied_improvements(),
        "youtube": auth_status(),
    }


@app.get("/api/youtube/status")
async def youtube_status() -> dict:
    return auth_status()


@app.get("/api/learned")
async def learned_file() -> dict:
    return {"content": LearnedFile(settings.learned_path).read_tail()}


@app.get("/api/journal")
async def journal() -> dict:
    return {"entries": get_memory().learning_journal(limit=20)}


@app.get("/api/dev")
async def list_dev() -> dict:
    memory = get_memory()
    return {
        "pending": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "pros": t.pros,
                "cons": t.cons,
            }
            for t in memory.list_dev_tasks(status="pending")
        ]
    }


@app.post("/api/dev")
async def create_dev(body: DevRequest) -> dict:
    if not body.title.strip() or not body.description.strip():
        raise HTTPException(400, "Title and description required")
    task = get_memory().create_dev_task(title=body.title.strip(), description=body.description.strip())
    return {"id": task.id, "message": f"Dev task #{task.id} queued for approval"}


@app.post("/api/dev/{task_id}/yes")
async def approve_dev(task_id: int, body: ImprovementDecision) -> dict:
    memory = get_memory()
    try:
        task = memory.review_dev_task(task_id, approved=True, note=body.note or "Approved.")
    except KeyError:
        raise HTTPException(404, "Not found") from None
    LearnedFile(settings.learned_path).record_dev_task(task, approved=True)
    return {"status": task.status, "title": task.title}


@app.post("/api/dev/{task_id}/no")
async def reject_dev(task_id: int, body: ImprovementDecision) -> dict:
    memory = get_memory()
    try:
        task = memory.review_dev_task(task_id, approved=False, note=body.note or "Rejected.")
    except KeyError:
        raise HTTPException(404, "Not found") from None
    return {"status": task.status, "title": task.title}


@app.post("/api/production")
async def create_production_pack(body: ProductionRequest) -> dict:
    from shorts_bot.services.ops import BotOperations

    return BotOperations().prepare_video_production(body.draft_id, body.turboscribe_text)


@app.post("/api/youtube/apply-brand")
async def youtube_apply_brand() -> dict:
    from shorts_bot.services.ops import BotOperations

    result = BotOperations().apply_channel_branding()
    return result


@app.post("/api/youtube/sync")
async def youtube_sync() -> dict:
    result = get_analytics_sync().run()
    pending = len(get_memory().list_improvements(status="pending"))
    return {
        "ok": result.ok,
        "message": result.message,
        "videos_scored": result.videos_scored,
        "improvements_created": result.improvements_created,
        "rewards": result.rewards or [],
        "pending_improvements": pending,
        "sign_off_hint": "Tap Yes on the right — one tap each." if pending else None,
    }
