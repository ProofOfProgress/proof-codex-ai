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


@app.get("/api/agent-ops/missions")
def agent_ops_missions(limit: int = 20) -> dict:
    from shorts_bot.agent_ops.log import list_missions

    return {"missions": list_missions(limit=min(limit, 50))}


@app.get("/api/agent-ops/missions/{mission_id}")
def agent_ops_mission_detail(mission_id: str) -> dict:
    from shorts_bot.agent_ops.log import mission_summary

    summary = mission_summary(mission_id)
    if not summary:
        return JSONResponse(status_code=404, content={"error": "mission not found"})
    return summary


@app.get("/agent-ops", response_class=HTMLResponse)
def agent_ops_dashboard(mission: str = "") -> str:
    return _AGENT_OPS_HTML.replace("__MISSION__", mission or "")


_AGENT_OPS_HTML = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Team — Mission Log</title>
<style>
  body{font-family:system-ui,sans-serif;margin:0;background:#0f1117;color:#e6edf3}
  header{padding:1rem 1.5rem;border-bottom:1px solid #30363d;background:#161b22}
  h1{margin:0;font-size:1.25rem}
  .sub{color:#8b949e;font-size:.9rem;margin-top:.35rem}
  main{display:grid;grid-template-columns:280px 1fr;min-height:calc(100vh - 72px)}
  @media(max-width:768px){main{grid-template-columns:1fr}}
  aside{border-right:1px solid #30363d;padding:1rem;overflow:auto}
  section{padding:1rem 1.5rem;overflow:auto}
  .mission{padding:.6rem .75rem;border-radius:6px;cursor:pointer;margin-bottom:.4rem;border:1px solid transparent}
  .mission:hover{background:#21262d}
  .mission.active{background:#21262d;border-color:#388bfd}
  .mission small{display:block;color:#8b949e;font-size:.75rem;margin-top:.2rem}
  .event{padding:.55rem 0;border-bottom:1px solid #21262d;font-size:.9rem}
  .event .ts{color:#8b949e;font-size:.75rem}
  .event .who{color:#79c0ff;font-weight:600}
  .event .ev{color:#ffa657}
  .event .msg{color:#c9d1d9;margin-top:.15rem}
  .badge{display:inline-block;padding:.1rem .45rem;border-radius:999px;font-size:.7rem;background:#238636;margin-left:.5rem}
  a{color:#58a6ff}
</style>
</head><body>
<header>
  <h1>Agent Team <span class="badge" id="live">live</span></h1>
  <div class="sub">CEO ↔ employee mission log · refreshes every 5s · <a href="/">factory home</a></div>
</header>
<main>
  <aside><div id="missions">Loading missions…</div></aside>
  <section><div id="feed">Select a mission</div></section>
</main>
<script>
const initialMission = "__MISSION__";
let active = initialMission;

async function loadMissions(){
  const r = await fetch('/api/agent-ops/missions');
  const data = await r.json();
  const box = document.getElementById('missions');
  if(!data.missions.length){ box.innerHTML='<p>No missions yet. Ask the main agent to run a pipeline — it will create a mission log.</p>'; return; }
  box.innerHTML = data.missions.map(m => `
    <div class="mission ${m.mission_id===active?'active':''}" data-id="${m.mission_id}">
      <strong>${esc(m.name||m.mission_id)}</strong>
      <small>${m.mission_id} · ${m.updated_at}<br>${(m.agents||[]).join(', ')}</small>
    </div>`).join('');
  box.querySelectorAll('.mission').forEach(el=>{
    el.onclick = ()=>{ active = el.dataset.id; loadMissions(); loadFeed(); };
  });
  if(!active && data.missions[0]) active = data.missions[0].mission_id;
}

async function loadFeed(){
  if(!active){ document.getElementById('feed').innerHTML='Select a mission'; return; }
  const r = await fetch('/api/agent-ops/missions/'+active);
  if(!r.ok){ document.getElementById('feed').innerHTML='Mission not found'; return; }
  const m = await r.json();
  const events = (m.events||[]).slice().reverse();
  document.getElementById('feed').innerHTML = `
    <h2 style="margin-top:0">${esc(m.name||active)}</h2>
    <p style="color:#8b949e">Mission <code>${active}</code> · ${m.events.length} events</p>
    ${events.map(e=>`
      <div class="event">
        <div><span class="ts">${esc(e.ts||'')}</span>
        <span class="who">${esc(e.agent||'?')}</span>
        <span class="ev">${esc(e.event||'?')}</span>
        ${e.target?'<span style="color:#8b949e"> → '+esc(e.target)+'</span>':''}</div>
        ${e.message?'<div class="msg">'+esc(e.message)+'</div>':''}
      </div>`).join('')}`;
}

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;'); }

async function tick(){ await loadMissions(); await loadFeed(); }
tick();
setInterval(tick, 5000);
</script>
</body></html>"""


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
<li><a href="/agent-ops">/agent-ops</a> — CEO ↔ employee mission log</li>
</ul>
<p>Self-learning: POST <code>/api/score</code> with clip metrics from TikTok analytics.</p>
<p>CLI: <code>python3 -m shorts_bot.tiktok_shop status</code></p>
<p>Score CLI: <code>python3 -m shorts_bot.learning.score_cli score --label "Product clip" --swipe 65 --retention 40 --views 1200 --reflect</code></p>
</body></html>"""


@app.exception_handler(Exception)
async def unhandled_exception(_request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(exc)})
