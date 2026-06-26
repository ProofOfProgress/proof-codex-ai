"""90-day blueprint audit — prove self-learning loop is wired (on paper)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.learning.workflow import load_active_workflow
from shorts_bot.learning.workflow_store import WorkflowRunStore
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.product_queue import load_product_queue


@dataclass
class AuditCheck:
    id: str
    label: str
    passed: bool
    detail: str
    kind: str = "software"  # software | operational


def _step_enabled(wf, step_id: str) -> bool:
    step = wf.step(step_id)
    return bool(step and step.enabled)


def run_blueprint_audit(*, store: MemoryStore | None = None) -> list[AuditCheck]:
    """Return checklist rows for docs/VIRAL_90_DAY_BLUEPRINT.md."""
    store = store or MemoryStore(settings.database_path)
    checks: list[AuditCheck] = []

    # 1 — Closed loop modules exist and are importable
    loop_ok = True
    loop_detail: list[str] = []
    for mod in (
        "shorts_bot.rewards.engine",
        "shorts_bot.learning.mem0_bridge",
        "shorts_bot.learning.public_evolve",
        "shorts_bot.learning.workflow_evolve",
        "shorts_bot.youtube.sync",
    ):
        try:
            __import__(mod)
            loop_detail.append(mod.split(".")[-1])
        except ImportError as exc:
            loop_ok = False
            loop_detail.append(f"missing:{mod} ({exc})")
    checks.append(
        AuditCheck(
            "closed_loop",
            "Closed loop: upload → analytics → memory → next script differs",
            loop_ok,
            " + ".join(loop_detail),
        )
    )

    # 2 — Versioned workflow
    wf_path = settings.data_dir / "workflows" / "daily_invideo_v1.json"
    wf = load_active_workflow(store)
    versioned = wf_path.is_file() and wf.version >= 1 and wf.id
    checks.append(
        AuditCheck(
            "versioned_workflow",
            "Versioned workflow (v1 vs vN auditable)",
            versioned,
            f"{wf.id} v{wf.version} @ {wf_path.name}",
        )
    )

    # 3 — No human gates in daily path (software side)
    auto_steps = ("auto_approve", "invideo_project", "youtube_upload")
    human_free = all(_step_enabled(wf, s) for s in auto_steps)
    checks.append(
        AuditCheck(
            "no_human_gates",
            "No human in daily path (auto-approve + upload steps on)",
            human_free,
            ", ".join(f"{s}={'on' if _step_enabled(wf, s) else 'off'}" for s in auto_steps),
        )
    )

    # 4 — QC before spend
    qc_on = settings.script_qc_enabled and _step_enabled(wf, "script_qc")
    checks.append(
        AuditCheck(
            "qc_before_spend",
            "QC before spend (script QC blocks bad briefs)",
            qc_on,
            f"flag={settings.script_qc_enabled} step={'on' if _step_enabled(wf, 'script_qc') else 'off'} "
            f"min={settings.script_qc_min_score}",
        )
    )

    # 5 — Audit trail
    telemetry_dir = settings.data_dir / "telemetry"
    mem0_dir = settings.data_dir / "mem0"
    trail = settings.run_telemetry_enabled and settings.mem0_enabled
    run_count = len(WorkflowRunStore(store).recent(limit=100))
    checks.append(
        AuditCheck(
            "audit_trail",
            "Audit trail (telemetry JSONL + Mem0 recall)",
            trail,
            f"telemetry={telemetry_dir} mem0={mem0_dir} workflow_runs={run_count}",
        )
    )

    # 6 — Niche locked
    queue_path = settings.data_dir / "product_queue.json"
    try:
        queue = load_product_queue(queue_path)
        niche_ok = len(queue) >= 10 and all(q.product for q in queue[:5])
        niche_detail = f"{len(queue)} products queued @ {queue_path.name}"
    except Exception as exc:
        niche_ok = False
        niche_detail = str(exc)
    checks.append(
        AuditCheck(
            "niche_locked",
            "Niche locked (product queue, not random topics)",
            niche_ok,
            niche_detail,
        )
    )

    # 7 — Failure modes
    retries = settings.invideo_render_retries >= 2
    try:
        from shorts_bot.learning.public_evolve import match_credit_fail, match_render_timeout

        failure_ok = retries and callable(match_credit_fail) and callable(match_render_timeout)
    except ImportError:
        failure_ok = False
    checks.append(
        AuditCheck(
            "failure_modes",
            "Failure modes handled (credit fail detect + render retry ×2)",
            failure_ok,
            f"invideo_render_retries={settings.invideo_render_retries}",
        )
    )

    # Operational — credits / daily loop (not a software gap)
    daily_blocked = not settings.auto_daily_enabled
    checks.append(
        AuditCheck(
            "daily_operational",
            "Legacy InVideo daily loop (retired — use tiktok_shop + course)",
            not daily_blocked,
            f"auto_daily_enabled={settings.auto_daily_enabled} pipeline={settings.pipeline_backend} (expected: tiktok_shop, auto_daily=false)",
            kind="operational",
        )
    )

    return checks


def audit_score(checks: list[AuditCheck]) -> tuple[int, int, int]:
    software = [c for c in checks if c.kind == "software"]
    passed = sum(1 for c in software if c.passed)
    return passed, len(software), sum(1 for c in checks if c.kind == "operational" and not c.passed)


def format_audit_report(checks: list[AuditCheck]) -> str:
    passed, total, ops_blocked = audit_score(checks)
    lines = [
        "90-day blueprint audit",
        f"Software checklist: {passed}/{total} pass",
    ]
    if ops_blocked:
        lines.append(f"Operational blockers: {ops_blocked} (expected until credits/phone fixed)")
    lines.append("")
    for c in checks:
        mark = "✓" if c.passed else ("~" if c.kind == "operational" else "✗")
        lines.append(f"  [{mark}] {c.label}")
        lines.append(f"      {c.detail}")
    if passed == total:
        lines.append("")
        lines.append("On paper: self-learning loop is wired. Ship Shorts for analytics signal.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit 90-day viral blueprint wiring")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    checks = run_blueprint_audit()
    if args.json:
        print(
            json.dumps(
                {
                    "checks": [
                        {
                            "id": c.id,
                            "label": c.label,
                            "passed": c.passed,
                            "detail": c.detail,
                            "kind": c.kind,
                        }
                        for c in checks
                    ],
                    "software_passed": audit_score(checks)[0],
                    "software_total": audit_score(checks)[1],
                },
                indent=2,
            )
        )
        return

    print(format_audit_report(checks))


if __name__ == "__main__":
    main()
