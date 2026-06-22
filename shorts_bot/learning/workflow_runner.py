"""Execute the versioned daily InVideo workflow."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.invideo.generate import generate_from_prompt
from shorts_bot.invideo.prompts import shorts_product_brief
from shorts_bot.invideo.script_pack import draft_pack_dir
from shorts_bot.learning.workflow import (
    StepResult,
    WorkflowDefinition,
    WorkflowRun,
    load_active_workflow,
)
from shorts_bot.learning.workflow_evolve import evolve_after_daily_run
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.product_rotation import (
    consume_pending_queue_item,
    next_product_topic,
    product_name_from_topic,
)


@dataclass
class DailyWorkflowResult:
    ok: bool
    draft_id: int
    topic: str
    project_url: str
    video_path: Path | None
    upload_url: str | None
    messages: list[str]
    workflow_run: WorkflowRun
    evolution_summary: str

    @property
    def summary(self) -> str:
        lines = list(self.messages)
        if self.evolution_summary:
            lines.append(f"Workflow evolution: {self.evolution_summary}")
        return "\n".join(lines)


def _record_step(step_id: str, ok: bool, detail: str = "", t0: float = 0.0) -> StepResult:
    return StepResult(
        step_id=step_id,
        ok=ok,
        detail=detail,
        duration_sec=time.monotonic() - t0 if t0 else 0.0,
    )


def invideo_recovery_lines(draft_id: int, project_url: str) -> list[str]:
    """Commands for recovering an InVideo project after cloud/browser blockers."""
    lines = [
        f"Recovery draft #{draft_id}: {project_url}",
        "Login/check InVideo: python3 -m shorts_bot.invideo.handoff_cli",
        f"Retry download: python3 -m shorts_bot.invideo.ship_cli --draft-id {draft_id}",
        (
            "If exported elsewhere, import it: "
            f"python3 -m shorts_bot.invideo.fetch_url_cli --draft-id {draft_id} 'DRIVE_OR_MP4_URL'"
        ),
    ]
    return lines


def run_daily_invideo_workflow(
    store: MemoryStore,
    *,
    topic: str | None = None,
    upload: bool | None = None,
    wait_render_sec: int | None = None,
    workflow: WorkflowDefinition | None = None,
) -> DailyWorkflowResult:
    """Run daily Short using the active (evolvable) workflow definition."""
    wf = workflow or load_active_workflow(store)
    messages: list[str] = [f"Workflow {wf.id} v{wf.version}"]

    step_results: list[StepResult] = []
    draft_id = 0
    project_url = ""
    video_path: Path | None = None
    upload_url: str | None = None
    product = ""
    brief = ""
    hook = ""
    verdict = "Pay, Skip, or Wait"

    # --- pick_topic ---
    if wf.step("pick_topic") and wf.step("pick_topic").enabled:
        t0 = time.monotonic()
        try:
            topic = topic or next_product_topic(store)
            product = product_name_from_topic(topic)
            step_results.append(_record_step("pick_topic", True, topic, t0))
            messages.extend([f"Product: {product}", f"Topic: {topic}"])
        except Exception as exc:
            step_results.append(_record_step("pick_topic", False, str(exc), t0))
            return _finalize(store, wf, step_results, messages, 0, topic or "", "", None, None, upload)

    # --- build_brief ---
    brief_step = wf.step("build_brief")
    if brief_step and brief_step.enabled:
        t0 = time.monotonic()
        try:
            hook_tpl = str(brief_step.params.get("hook_template", HOOK_TEMPLATES_FALLBACK))
            verdict = str(brief_step.params.get("verdict_hint", "Pay, Skip, or Wait"))
            pending = consume_pending_queue_item(store)
            if pending:
                if pending.get("hook"):
                    hook = str(pending["hook"])
                else:
                    hook = hook_tpl.format(product=product)
                if pending.get("verdict_hint"):
                    verdict = str(pending["verdict_hint"])
            else:
                hook = hook_tpl.format(product=product)
            brief = shorts_product_brief(
                product=product,
                hook=hook,
                verdict_hint=verdict,
                extra=f"Topic line for upload: {topic}",
            )
            step_results.append(_record_step("build_brief", True, hook[:120], t0))
        except Exception as exc:
            step_results.append(_record_step("build_brief", False, str(exc), t0))
            return _finalize(store, wf, step_results, messages, 0, topic or "", "", None, None, upload)

    # --- script_qc ---
    qc_step = wf.step("script_qc")
    if qc_step and qc_step.enabled:
        t0 = time.monotonic()
        from shorts_bot.learning.script_qc import score_script_brief

        qc = score_script_brief(
            product=product,
            hook=hook,
            brief=brief,
            verdict_hint=verdict,
        )
        if qc.passed:
            step_results.append(_record_step("script_qc", True, f"score={qc.score}", t0))
            messages.append(f"Script QC passed ({qc.score}/10)")
        else:
            detail = "; ".join(qc.issues) or qc.summary
            step_results.append(_record_step("script_qc", False, detail[:300], t0))
            messages.append(f"Script QC failed ({qc.score}/10): {detail[:200]}")
            return _finalize(
                store,
                wf,
                step_results,
                messages,
                0,
                topic or "",
                "",
                None,
                None,
                upload,
                ok=False,
            )

    # --- save_draft ---
    if wf.step("save_draft") and wf.step("save_draft").enabled:
        t0 = time.monotonic()
        try:
            draft = store.save_draft(
                topic=topic or product,
                script=brief,
                hook=hook,
                help_angle="Pay / Skip / Wait — honest 30s AI product review",
                quality_notes=f"InVideo daily workflow v{wf.version}",
            )
            draft_id = draft.id
            step_results.append(_record_step("save_draft", True, f"draft #{draft_id}", t0))
            messages.append(f"Draft #{draft_id} created")
        except Exception as exc:
            step_results.append(_record_step("save_draft", False, str(exc), t0))
            return _finalize(store, wf, step_results, messages, 0, topic or "", "", None, None, upload)

    # --- auto_approve ---
    approve_step = wf.step("auto_approve")
    if approve_step and approve_step.enabled and settings.auto_approve_drafts and draft_id:
        t0 = time.monotonic()
        try:
            store.review_draft(draft_id, "approved", "Auto-approved (InVideo daily workflow)")
            step_results.append(_record_step("auto_approve", True, "", t0))
            messages.append(f"Auto-approved draft #{draft_id}")
        except Exception as exc:
            step_results.append(_record_step("auto_approve", False, str(exc), t0))

    # --- invideo_project ---
    if wf.step("invideo_project") and wf.step("invideo_project").enabled:
        t0 = time.monotonic()
        try:
            gen = generate_from_prompt(brief, topic=topic, draft_id=draft_id)
            project_url = gen.project_url
            step_results.append(_record_step("invideo_project", True, project_url, t0))
            messages.append(f"InVideo project: {project_url}")
        except Exception as exc:
            step_results.append(_record_step("invideo_project", False, str(exc)[:300], t0))
            return _finalize(
                store, wf, step_results, messages, draft_id, topic or "", project_url, None, None, upload
            )

    pack = draft_pack_dir(draft_id)
    video_path = pack / "final_short.mp4"

    # --- invideo_render ---
    render_step = wf.step("invideo_render")
    if render_step and render_step.enabled:
        t0 = time.monotonic()
        render_wait = wait_render_sec
        if render_wait is None:
            render_wait = int(render_step.params.get("wait_render_sec", 2400))
        try:
            from shorts_bot.invideo.ship_cli import ship

            last_err = ""
            attempts = max(1, int(settings.invideo_render_retries))
            for attempt in range(1, attempts + 1):
                try:
                    ship(project_url, video_path, wait_render_sec=render_wait)
                    step_results.append(
                        _record_step(
                            "invideo_render",
                            True,
                            f"{video_path} (attempt {attempt})",
                            t0,
                        )
                    )
                    messages.append(f"MP4 saved: {video_path}")
                    last_err = ""
                    break
                except Exception as exc:
                    last_err = str(exc)[:300]
                    if attempt < attempts:
                        messages.append(f"InVideo render attempt {attempt} failed — retrying…")
                        time.sleep(min(30 * attempt, 90))
            if last_err:
                raise RuntimeError(last_err)
        except Exception as exc:
            msg = str(exc)[:300]
            step_results.append(_record_step("invideo_render", False, msg, t0))
            messages.append(f"InVideo render/download: {msg}")
            from shorts_bot.automation.alerts import record_automation_alert

            record_automation_alert(
                "invideo_daily",
                msg,
                detail=(
                    f"draft={draft_id} project={project_url} workflow=v{wf.version} — "
                    " | ".join(invideo_recovery_lines(draft_id, project_url))
                ),
            )

    has_video = video_path.is_file() and video_path.stat().st_size > 50_000

    # --- drive_inbox (laptop export → Drive folder → auto pull) ---
    if not has_video:
        t0 = time.monotonic()
        try:
            from shorts_bot.drive.inbox import try_pull_for_draft

            pull = try_pull_for_draft(draft_id)
            if pull and pull.video_path:
                video_path = pull.video_path
                has_video = True
                step_results.append(
                    _record_step("drive_inbox", True, pull.message[:300], t0)
                )
                messages.append(pull.message)
        except Exception as exc:
            step_results.append(_record_step("drive_inbox", False, str(exc)[:300], t0))

    # --- youtube_upload ---
    upload_step = wf.step("youtube_upload")
    do_upload = settings.auto_upload_youtube if upload is None else upload
    if upload_step and upload_step.enabled and has_video and do_upload:
        t0 = time.monotonic()
        try:
            from shorts_bot.production.upload_canonical_cli import upload_canonical

            upload_url = upload_canonical(draft_id, video_path)
            store.review_draft(draft_id, "published", upload_url or "uploaded")
            step_results.append(_record_step("youtube_upload", True, upload_url or "", t0))
            messages.append(f"PUBLISHED: {upload_url}")
        except Exception as exc:
            step_results.append(_record_step("youtube_upload", False, str(exc)[:300], t0))
            messages.append(f"YouTube upload failed: {exc}")
            has_video = False
    elif not has_video:
        messages.append("No MP4 on disk — stopped before upload.")
        if draft_id and project_url:
            messages.extend(invideo_recovery_lines(draft_id, project_url))
        else:
            messages.append("Drop MP4 in Drive inbox or paste Drive link for fetch_url_cli.")

    ok = bool(upload_url) if do_upload else has_video
    return _finalize(
        store,
        wf,
        step_results,
        messages,
        draft_id,
        topic or "",
        project_url,
        video_path if has_video else None,
        upload_url,
        upload,
        ok=ok,
    )


HOOK_TEMPLATES_FALLBACK = "Everyone's paying for {product} — I tested if it's worth it."


def _finalize(
    store: MemoryStore,
    wf: WorkflowDefinition,
    step_results: list[StepResult],
    messages: list[str],
    draft_id: int,
    topic: str,
    project_url: str,
    video_path: Path | None,
    upload_url: str | None,
    upload: bool | None,
    *,
    ok: bool | None = None,
) -> DailyWorkflowResult:
    do_upload = settings.auto_upload_youtube if upload is None else upload
    if ok is None:
        ok = bool(upload_url) if do_upload else bool(video_path)

    run = WorkflowRun(
        workflow_id=wf.id,
        workflow_version=wf.version,
        draft_id=draft_id or None,
        topic=topic,
        ok=ok,
        step_results=step_results,
    )

    from shorts_bot.memory.extensions import MemoryExtensions

    memory = MemoryExtensions(store)
    evo = evolve_after_daily_run(store, run, memory=memory)

    from shorts_bot.learning.run_telemetry import record_run

    record_run(run, evolution_summary=evo.summary())

    return DailyWorkflowResult(
        ok=ok,
        draft_id=draft_id,
        topic=topic,
        project_url=project_url,
        video_path=video_path,
        upload_url=upload_url,
        messages=messages,
        workflow_run=run,
        evolution_summary=evo.summary(),
    )
