"""Build today's product list and mission plan."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from shorts_bot.daily_prelaunch.paths import today_plan_path
from shorts_bot.daily_prelaunch.prompt import load_config


def create_mission_id(*, name: str) -> str:
    from shorts_bot.agent_ops.log import new_mission

    return new_mission(name, owner="daily_prelaunch")


def _recent_product_names(*, days: int = 3) -> set[str]:
    """Products already used in recent plans — avoid repeats."""
    from shorts_bot.daily_prelaunch.paths import prelaunch_dir

    used: set[str] = set()
    root = prelaunch_dir()
    if not root.is_dir():
        return used
    for path in sorted(root.glob("*_plan.json"))[-days:]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for name in data.get("products") or []:
                used.add(str(name).strip().lower())
        except (json.JSONDecodeError, OSError):
            continue
    plan = today_plan_path()
    if plan.is_file():
        try:
            data = json.loads(plan.read_text(encoding="utf-8"))
            for name in data.get("products") or []:
                used.add(str(name).strip().lower())
        except json.JSONDecodeError:
            pass
    return used


def scout_product_names(*, limit: int = 10) -> tuple[list[str], str]:
    """Refresh scout if possible; return product names + status note."""
    try:
        from shorts_bot.tiktok_shop.product_scout import load_products, save_products, scout_products

        products = scout_products(limit=limit)
        if products:
            save_products(products)
            names = [p.product_name for p in products]
            return names, f"scout refreshed ({len(names)} products)"
        rows = load_products()
        if rows:
            names = [str(r.get("product_name") or r.get("name") or "") for r in rows]
            names = [n for n in names if n.strip()]
            return names, f"loaded {len(names)} from products.json (scout returned empty)"
        return [], "no products — FastMoss scout not configured or returned nothing"
    except Exception as exc:
        try:
            from shorts_bot.tiktok_shop.product_scout import load_products

            rows = load_products()
            names = [
                str(r.get("product_name") or r.get("name") or "")
                for r in rows
                if (r.get("product_name") or r.get("name"))
            ]
            if names:
                return names, f"scout error ({exc}); using products.json ({len(names)})"
        except Exception:
            pass
        return [], f"scout failed: {exc}"


def pick_today_products(all_names: list[str], *, target: int) -> list[str]:
    recent = _recent_product_names()
    picked: list[str] = []
    for name in all_names:
        if not name.strip():
            continue
        if name.strip().lower() in recent:
            continue
        picked.append(name.strip())
        if len(picked) >= target:
            break
    if len(picked) < target:
        for name in all_names:
            if name.strip() and name.strip() not in picked:
                picked.append(name.strip())
            if len(picked) >= target:
                break
    return picked[:target]


def build_plan(*, mission_id: str | None = None) -> dict:
    cfg = load_config()
    target = int(cfg.get("clips_target", 8))
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mission_name = f"Daily pre-launch {day}"
    mid = mission_id or create_mission_id(name=mission_name)

    all_names, scout_note = scout_product_names(limit=max(15, target + 5))
    products = pick_today_products(all_names, target=target)

    plan = {
        "date": day,
        "mission_id": mid,
        "mission_name": mission_name,
        "clips_target": target,
        "products": products,
        "scout_note": scout_note,
        "prelaunch_mode": bool(cfg.get("prelaunch_mode", True)),
        "post_to_zernio": False,
        "account_id": "affiliate_main",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": [
            "product-researcher (if plan empty)",
            "module4 sample",
            "product-video-prompt-builder",
            "Kling render",
            "video-editor",
            "module1-qc-runner",
            "queue locally",
        ],
    }
    return plan


def save_plan(plan: dict) -> Path:
    path = today_plan_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    archive = path.parent / f"{plan.get('date', 'unknown')}_plan.json"
    archive.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return path
