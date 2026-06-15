from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
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
    run_full_automation,
)
from shorts_bot.web.auth import ApiTokenMiddleware
from shorts_bot.youtube.google_auth import auth_status

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from shorts_bot.automation.background import start_background_automation

    stop = await start_background_automation()
    yield
    stop.set()
    from shorts_bot.automation.background import _stop_slack_autonomy_bus

    await asyncio.to_thread(_stop_slack_autonomy_bus)
    await asyncio.sleep(0.1)


app = FastAPI(title="Peripheral Operator", version="0.7.0", lifespan=lifespan)
app.add_middleware(ApiTokenMiddleware)


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


class ManagerRequest(BaseModel):
    message: str
    force_async: bool = False


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


def _draft_pack_dir(draft_id: int) -> Path:
    return settings.data_dir / "production" / f"draft_{draft_id}"


def _safe_pack_file(pack: Path, name: str) -> Path:
    """Resolve a file inside a draft pack — blocks path traversal."""
    clean = Path(name).name
    if not clean or clean != name:
        raise HTTPException(400, "Invalid file name")
    path = (pack / clean).resolve()
    if not str(path).startswith(str(pack.resolve())):
        raise HTTPException(400, "Invalid path")
    if not path.is_file():
        raise HTTPException(404, "File not found")
    return path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_creature_glb() -> Path | None:
    from shorts_bot.production.blender.creature_paths import resolve_creature_model

    hit = resolve_creature_model()
    if hit and hit.suffix.lower() == ".glb" and hit.is_file():
        return hit.resolve()
    # Prefer glb next to fbx
    if hit:
        glb = hit.with_suffix(".glb")
        if glb.is_file():
            return glb.resolve()
    root = _repo_root()
    for candidate in (
        root / "channel/assets/creatures/scp_096/scp_096.glb",
        root / "channel/assets/creatures/scp_096.glb",
    ):
        if candidate.is_file():
            return candidate.resolve()
    return None


@app.get("/workspace/draft/{draft_id}/creature.glb")
async def workspace_creature_model(draft_id: int) -> FileResponse:
    """Serve creature GLB for browser 3D workspace."""
    path = _safe_creature_glb()
    if not path:
        raise HTTPException(404, "Creature GLB not found")
    return FileResponse(path, media_type="model/gltf-binary")


@app.get("/workspace/draft/{draft_id}", response_class=HTMLResponse)
async def workspace_page(request: Request, draft_id: int) -> HTMLResponse:
    pack = _draft_pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)
    creature_url = f"/workspace/draft/{draft_id}/creature.glb"
    if _safe_creature_glb() is None:
        creature_url = ""
    return TEMPLATES.TemplateResponse(
        request,
        "workspace.html",
        {
            "draft_id": draft_id,
            "creature_url": creature_url,
            "api_token": (settings.web_api_token or "").strip() or None,
        },
    )


class SceneLayoutPatch(BaseModel):
    creature: dict | None = None
    camera: dict | None = None
    environment: dict | None = None


@app.get("/api/workspace/draft/{draft_id}/scene")
async def get_scene_layout(draft_id: int) -> dict:
    from shorts_bot.production.blender.scene_layout import load_scene_layout

    pack = _draft_pack_dir(draft_id)
    return load_scene_layout(pack, draft_id=draft_id)


@app.get("/api/workspace/draft/{draft_id}/scene/default")
async def get_scene_layout_default(draft_id: int) -> dict:
    from shorts_bot.production.blender.scene_layout import DEFAULT_LAYOUT

    return {**DEFAULT_LAYOUT, "draft_id": draft_id}


@app.put("/api/workspace/draft/{draft_id}/scene")
async def put_scene_layout(draft_id: int, body: SceneLayoutPatch) -> dict:
    from shorts_bot.production.blender.scene_layout import (
        load_scene_layout,
        merge_layout_update,
        save_scene_layout,
    )

    pack = _draft_pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)
    existing = load_scene_layout(pack, draft_id=draft_id)
    patch = body.model_dump(exclude_none=True)
    merged = merge_layout_update(existing, patch)
    merged["draft_id"] = draft_id
    save_scene_layout(pack, merged, updated_by="owner")
    return merged


@app.websocket("/ws/workspace/{draft_id}")
async def workspace_ws(websocket: WebSocket, draft_id: int) -> None:
    from shorts_bot.production.blender.scene_layout import (
        load_scene_layout,
        merge_layout_update,
        save_scene_layout,
    )
    from shorts_bot.web.workspace_hub import workspace_hub

    expected = (settings.web_api_token or "").strip()
    if expected:
        token = websocket.query_params.get("token") or websocket.headers.get("x-api-token")
        if token != expected:
            await websocket.close(code=4401)
            return

    await workspace_hub.connect(draft_id, websocket)
    pack = _draft_pack_dir(draft_id)
    layout = load_scene_layout(pack, draft_id=draft_id)
    await websocket.send_json({"type": "layout", "layout": layout})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            mtype = msg.get("type")
            if mtype in ("transform", "transform_live"):
                patch = {
                    k: msg[k]
                    for k in ("creature", "camera", "environment")
                    if isinstance(msg.get(k), dict)
                }
                if patch and mtype == "transform":
                    existing = load_scene_layout(pack, draft_id=draft_id)
                    merged = merge_layout_update(existing, patch)
                    merged["draft_id"] = draft_id
                    save_scene_layout(pack, merged, updated_by="workspace")
                    layout = merged
                await workspace_hub.broadcast(
                    draft_id,
                    {"type": mtype, **patch},
                    skip=websocket,
                )
            elif mtype == "saved" and isinstance(msg.get("layout"), dict):
                await workspace_hub.broadcast(draft_id, msg, skip=websocket)
    except WebSocketDisconnect:
        pass
    finally:
        await workspace_hub.disconnect(draft_id, websocket)


@app.get("/preview/draft/{draft_id}/preflight/{filename}")
async def preview_draft_preflight(draft_id: int, filename: str) -> FileResponse:
    """Peak still + preflight QC artifacts."""
    pack = _draft_pack_dir(draft_id)
    preflight = pack / "preflight"
    if not preflight.is_dir():
        raise HTTPException(404, "Preflight folder not found")
    path = _safe_pack_file(preflight, filename)
    media = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".json": "application/json",
    }
    return FileResponse(
        path,
        media_type=media.get(path.suffix.lower(), "application/octet-stream"),
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/preview/draft/{draft_id}/file/{filename}")
async def preview_draft_file(draft_id: int, filename: str) -> FileResponse:
    """Stream a pack video or image for in-browser preview."""
    from shorts_bot.production.blender.preview_validate import is_browser_playable_mp4

    pack = _draft_pack_dir(draft_id)
    if not pack.is_dir():
        raise HTTPException(404, "Draft pack not found")
    path = _safe_pack_file(pack, filename)
    if path.suffix.lower() == ".mp4" and not is_browser_playable_mp4(path):
        raise HTTPException(409, "Video still rendering or corrupt — try another clip")
    media = {
        ".mp4": "video/mp4",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    return FileResponse(
        path,
        media_type=media.get(path.suffix.lower(), "application/octet-stream"),
        headers={"Accept-Ranges": "bytes", "Cache-Control": "no-cache"},
    )


@app.get("/preview/draft/{draft_id}/clips/{filename}")
async def preview_draft_clip(draft_id: int, filename: str) -> FileResponse:
    from shorts_bot.production.blender.preview_validate import is_browser_playable_mp4

    pack = _draft_pack_dir(draft_id)
    clips = pack / "clips"
    if not clips.is_dir():
        raise HTTPException(404, "Clips folder not found")
    path = _safe_pack_file(clips, filename)
    if not is_browser_playable_mp4(path):
        raise HTTPException(409, "Clip still rendering — wait for render to finish")
    return FileResponse(
        path,
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes", "Cache-Control": "no-cache"},
    )


@app.get("/preview/draft/{draft_id}/frames/{filename}")
async def preview_draft_frame(draft_id: int, filename: str) -> FileResponse:
    pack = _draft_pack_dir(draft_id)
    frames = pack / "preview_frames"
    if not frames.is_dir():
        raise HTTPException(404, "Preview frames not found")
    path = _safe_pack_file(frames, filename)
    return FileResponse(path, media_type="image/png")


@app.get("/preview/draft/{draft_id}", response_class=HTMLResponse)
async def preview_draft_page(
    request: Request, draft_id: int, file: str | None = None, preflight: int | None = None
) -> HTMLResponse:
    """Browser page to watch draft videos — Cursor cannot open .mp4 in the editor."""
    from shorts_bot.production.blender.preview_validate import is_browser_playable_mp4, list_playable_clips

    pack = _draft_pack_dir(draft_id)
    if not pack.is_dir():
        raise HTTPException(404, f"No production pack for draft {draft_id}")

    import time
    cache_bust = int(time.time())

    videos: list[dict] = []
    final = pack / "final_short.mp4"
    if final.is_file() and is_browser_playable_mp4(final):
        manifest_path = pack / "manifest.json"
        micro = False
        if manifest_path.is_file():
            import json

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            micro = manifest.get("render_mode") == "micro_jumpscare" or manifest.get(
                "content_format"
            ) == "micro_jumpscare"
        label = "Micro jumpscare (3s) 🔊" if micro else "Full Short (30s)"
        videos.append({
            "name": "final_short.mp4",
            "label": label,
            "url": f"/preview/draft/{draft_id}/file/final_short.mp4?v={cache_bust}",
        })
    for clip in list_playable_clips(pack / "clips"):
        videos.append({
            "name": f"clips/{clip.name}",
            "label": f"Clip — {clip.name}",
            "url": f"/preview/draft/{draft_id}/clips/{clip.name}?v={cache_bust}",
        })

    selected = None
    if file:
        for v in videos:
            if v["name"] == file or v["name"].endswith(f"/{file}") or v["name"] == f"clips/{file}":
                selected = v
                break
    if selected is None and videos:
        # Default: final_short (micro or full), else wave clip
        for v in videos:
            if v["name"] == "final_short.mp4":
                selected = v
                break
        if selected is None:
            for v in videos:
                if "wave" in v["name"] or "part_02" in v["name"]:
                    selected = v
                    break
        if selected is None:
            selected = videos[0]

    frames_dir = pack / "preview_frames"
    frames = []
    if frames_dir.is_dir():
        for img in sorted(frames_dir.glob("*.png")):
            frames.append({"name": img.name, "url": f"/preview/draft/{draft_id}/frames/{img.name}"})

    preflight_still = pack / "preflight" / "peak_still.jpg"
    preflight_info: dict | None = None
    if preflight_still.is_file():
        qc_path = pack / "preflight" / "preflight_qc.json"
        stamp_path = pack / "preview_build.json"
        score = None
        passed = None
        issues: list[str] = []
        build_note = ""
        built_at = cache_bust
        if stamp_path.is_file():
            import json

            try:
                stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
                built_at = stamp.get("built_at", built_at)
                params = stamp.get("params") or {}
                if params:
                    yaw = params.get("creature_yaw", "?")
                    build_note = (
                        f"Render stamp: yaw={yaw:.2f} gap={params.get('stop_gap')} "
                        f"cam_y={params.get('camera_y')} focal={params.get('focal_mm')}mm"
                    )
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        if qc_path.is_file():
            import json

            try:
                qc = json.loads(qc_path.read_text(encoding="utf-8"))
                score = qc.get("score")
                passed = qc.get("passed")
                issues = list(qc.get("issues") or [])[:4]
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        preflight_info = {
            "url": f"/preview/draft/{draft_id}/preflight/peak_still.jpg?v={built_at}",
            "score": score,
            "passed": passed,
            "issues": issues,
            "build_note": build_note,
        }

    show_preflight = bool(preflight) or file == "peak_still.jpg"

    render_busy = any(
        (pack / "clips").glob("blender_part_*0001-*.mp4")
    ) if (pack / "clips").is_dir() else False

    return TEMPLATES.TemplateResponse(
        request,
        "preview.html",
        {
            "draft_id": draft_id,
            "videos": videos,
            "selected": selected,
            "frames": frames,
            "preflight": preflight_info,
            "show_preflight": show_preflight,
            "render_busy": render_busy,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    memory = get_memory()
    store = get_store()
    learned = LearnedFile(settings.learned_path)
    from shorts_bot.services.ops import BotOperations

    pending_imps = memory.list_improvements(status="pending")
    from shorts_bot.agents.identity import manager_name

    return TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "manager_name": manager_name(),
            "has_openai": settings.has_full_chat,
            "chat_provider": settings.chat_provider,
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
            "api_token": (settings.web_api_token or "").strip() or None,
        },
    )


@app.get("/health")
async def health() -> dict:
    store = get_store()
    memory = get_memory()
    return {
        "ok": True,
        "version": __version__,
        "openai": settings.has_full_chat,
        "chat_provider": settings.chat_provider,
        "gemini": settings.has_gemini,
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
        from shorts_bot.agents.duration import parse_work_duration
        from shorts_bot.agents.manager import should_use_manager
        from shorts_bot.services.ops import BotOperations

        msg = body.message.strip()
        if should_use_manager(msg):
            parsed = parse_work_duration(msg)
            budget = parsed.work_seconds or 0
            if budget >= settings.manager_async_threshold_seconds:
                return await manager_run(
                    ManagerRequest(message=msg, force_async=True),
                )
            result = BotOperations().manager_chat(msg)
            return {"reply": result["reply"], "manager": result}
        reply = BotOperations().chat(msg)
        return {"reply": reply}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"Chat error: {exc}") from exc


@app.post("/api/manager/run")
async def manager_run(body: ManagerRequest) -> dict:
    """Chief Manager — sync for short budgets, async job for long work."""
    if not body.message.strip():
        raise HTTPException(400, "Empty message")
    if len(body.message) > 8000:
        raise HTTPException(400, "Message too long")

    from shorts_bot.agents.duration import clamp_work_seconds, parse_work_duration
    from shorts_bot.agents.job_runner import start_manager_job
    from shorts_bot.agents.job_store import ManagerJobStore
    from shorts_bot.agents.manager import strip_manager_prefix
    from shorts_bot.services.ops import BotOperations

    msg = body.message.strip()
    parsed = parse_work_duration(strip_manager_prefix(msg))
    budget = parsed.work_seconds or 0

    use_async = body.force_async or budget >= settings.manager_async_threshold_seconds

    if use_async and budget > 0:
        store = ManagerJobStore(settings.database_path)
        job = store.create(msg, work_seconds=budget)
        start_manager_job(store, job.id)
        return {
            "async": True,
            "job_id": job.id,
            "status": "queued",
            "work_seconds": budget,
            "poll": f"/api/manager/jobs/{job.id}",
        }

    result = await asyncio.to_thread(BotOperations().manager_chat, msg)
    return {"async": False, "manager": result, "reply": result["reply"]}


@app.get("/api/manager/jobs/{job_id}")
async def manager_job(job_id: str) -> dict:
    from shorts_bot.agents.job_store import ManagerJobStore

    try:
        job = ManagerJobStore(settings.database_path).get(job_id)
    except KeyError as exc:
        raise HTTPException(404, "Job not found") from exc
    return job.to_dict()


@app.get("/api/manager/jobs")
async def manager_jobs_list() -> dict:
    from shorts_bot.agents.job_store import ManagerJobStore

    jobs = ManagerJobStore(settings.database_path).list_recent(limit=20)
    return {"jobs": [j.to_dict() for j in jobs]}


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
    from shorts_bot.learning.feedback import learn_from_draft

    learn_from_draft(get_memory(), d.topic, body.note or "Approved", "approved")
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
    from shorts_bot.learning.feedback import learn_from_draft

    learn_from_draft(get_memory(), d.topic, body.note, "rejected")
    return {"status": d.status}


@app.post("/api/score")
async def score_video(body: ScoreRequest) -> dict:
    metrics = {
        k: v
        for k, v in body.model_dump().items()
        if k != "video_label" and v is not None
    }
    from shorts_bot.learning.score_helpers import propose_reward_improvement

    engine = get_reward_engine()
    result = engine.score(body.video_label, metrics)
    improvement = None
    proposer = get_proposer()
    imp = propose_reward_improvement(get_memory(), proposer, result)
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


@app.get("/api/briefing")
async def morning_briefing() -> dict:
    from shorts_bot.briefing.builder import build_morning_briefing

    text = build_morning_briefing()
    return {"briefing": text}


@app.get("/api/slack/status")
async def slack_status() -> dict:
    from shorts_bot.integrations.slack import slack_setup_status

    return slack_setup_status()


@app.post("/api/slack/test")
async def slack_test_webhook() -> dict:
    from shorts_bot.integrations.slack import send_test_message

    ok, message = send_test_message()
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"ok": True, "message": message}


class SlackAutonomyRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=2000)
    note: str = ""
    thread_ts: str | None = None


@app.post("/api/slack/autonomy")
async def slack_autonomy_enqueue(body: SlackAutonomyRequest) -> dict:
    """Post [autonomy] command to Slack — Socket Mode listener executes it."""
    from shorts_bot.integrations.slack_autonomy import post_autonomy_command

    ok, message = post_autonomy_command(
        body.command,
        note=body.note,
        thread_ts=body.thread_ts,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"ok": True, "message": message}


@app.get("/api/checklist")
async def setup_checklist() -> dict:
    from shorts_bot.services.ops import BotOperations

    return {"items": BotOperations().setup_checklist()}


@app.get("/api/status")
async def status() -> dict:
    store = get_store()
    memory = get_memory()
    return {
        "openai": settings.has_full_chat,
        "chat_provider": settings.chat_provider,
        "gemini": settings.has_gemini,
        "channel": store.channel_summary(),
        "stats": store.stats(),
        "pending_improvements": len(memory.list_improvements(status="pending")),
        "pending_drafts": len(store.list_drafts(status="pending")),
        "pending_dev": len(memory.list_dev_tasks(status="pending")),
        "applied_training": memory.applied_improvements(),
        "youtube": auth_status(),
    }


@app.get("/api/youtube/status")
async def youtube_status() -> dict:
    return auth_status()


@app.get("/api/login-status")
async def login_status() -> dict:
    import asyncio

    from shorts_bot.login_status import full_status

    rows = await asyncio.to_thread(full_status)
    ready = sum(1 for r in rows if r["ready"])
    return {"ready": ready, "total": len(rows), "services": rows}


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


@app.post("/api/production/auto/{draft_id}")
async def auto_production(draft_id: int) -> dict:
    from shorts_bot.services.ops import BotOperations

    return BotOperations().auto_make_video(draft_id)


@app.post("/api/youtube/apply-brand")
async def youtube_apply_brand() -> dict:
    from shorts_bot.services.ops import BotOperations

    result = BotOperations().apply_channel_branding()
    return result


@app.post("/api/youtube/comments")
async def youtube_comments() -> dict:
    from shorts_bot.services.ops import BotOperations

    result = await asyncio.to_thread(BotOperations().run_comment_replies)
    return result


@app.get("/api/youtube/comments/pending")
async def youtube_comments_pending() -> dict:
    memory = get_memory()
    return {
        "pending": memory.count_comments_needing_human(),
        "items": memory.list_comments_needing_human(limit=20),
    }


@app.post("/api/youtube/sync")
async def youtube_sync() -> dict:
    automation = await asyncio.to_thread(run_full_automation)
    result = automation.sync
    pending = len(get_memory().list_improvements(status="pending"))
    msg = result.message
    if automation.improvements_auto_approved:
        msg += f" (auto-approved {automation.improvements_auto_approved})"
    return {
        "ok": result.ok,
        "message": msg,
        "videos_scored": result.videos_scored,
        "improvements_created": result.improvements_created,
        "improvements_auto_approved": automation.improvements_auto_approved,
        "videos_published": automation.videos_published,
        "rewards": result.rewards or [],
        "pending_improvements": pending,
        "sign_off_hint": "Tap Yes on risky proposals only." if pending else None,
    }
