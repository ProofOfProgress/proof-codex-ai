"""Score TikTok Shop clips and run the self-learning loop from the CLI."""

from __future__ import annotations

import argparse
import json
import sys

from shorts_bot.config import settings
from shorts_bot.learning.reflect import reflect_after_sync
from shorts_bot.learning.score_helpers import propose_reward_improvement
from shorts_bot.training.auto_approve import improvement_is_auto_approvable
from shorts_bot.training.proposer import ImprovementProposer
from shorts_bot.web.deps import get_agent_memory, get_memory, get_proposer, get_reward_engine


def _score_clip(args: argparse.Namespace) -> int:
    metrics = {
        k: v
        for k, v in {
            "video_id": args.video_id,
            "viewed_vs_swiped_away": args.swipe,
            "retention_rate": args.retention,
            "views": args.views,
            "likes": args.likes,
            "comments": args.comments,
            "swipe_source": args.swipe_source,
            "retention_source": args.retention_source,
            "metrics_source": "manual_cli",
        }.items()
        if v is not None
    }
    memory = get_memory()
    engine = get_reward_engine()
    result = engine.score(args.label, metrics)
    proposer = get_proposer()
    imp = propose_reward_improvement(memory, proposer, result)
    if imp and args.auto_approve and improvement_is_auto_approvable(imp):
        memory.review_improvement(imp.id, approved=True, note="Auto-approved (score CLI)")
    reflect = None
    if settings.self_training_enabled and args.reflect:
        reflect = reflect_after_sync(memory, [result], agent_memory_store=get_agent_memory())
    out = {
        "score": result.score,
        "verdict": result.verdict,
        "reason": result.reason,
        "diagnosis": result.diagnosis,
        "breakdown": result.breakdown,
        "improvement_id": imp.id if imp else None,
        "reflect": reflect.summary() if reflect else None,
    }
    print(json.dumps(out, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Self-learning score + reflect")
    sub = parser.add_subparsers(dest="cmd", required=True)

    score = sub.add_parser("score", help="Score clip metrics and propose improvements")
    score.add_argument("--label", required=True, help="Clip label (product name or post title)")
    score.add_argument("--video-id", default=None, help="TikTok video id when known")
    score.add_argument("--swipe", type=float, default=None, help="Viewed vs swiped away %")
    score.add_argument("--retention", type=float, default=None, help="Avg watch / completion %")
    score.add_argument("--views", type=int, default=0)
    score.add_argument("--likes", type=int, default=0)
    score.add_argument("--comments", type=int, default=0)
    score.add_argument(
        "--swipe-source",
        default="manual",
        choices=("manual", "tiktok", "studio", "unavailable"),
    )
    score.add_argument(
        "--retention-source",
        default="manual",
        choices=("manual", "tiktok", "studio", "analytics_api"),
    )
    score.add_argument("--reflect", action="store_true", help="Run reflect loop after score")
    score.add_argument("--auto-approve", action="store_true", default=True)
    score.set_defaults(func=_score_clip)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
