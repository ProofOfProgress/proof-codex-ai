#!/usr/bin/env python3
"""Run pre-publish gate from shell — use before manual Zernio uploads."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from shorts_bot.tiktok_shop.pre_publish_gate import run_pre_publish_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-publish gate (cheap fast tier or standard+vision)")
    parser.add_argument("--type", choices=("video", "carousel", "affiliate"), default="video")
    parser.add_argument("--tier", choices=("fast", "standard", "full"), default="")
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--slide1", type=Path, default=None)
    parser.add_argument("--slide2", type=Path, default=None)
    parser.add_argument("--caption", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--product", default="")
    parser.add_argument("--account", default="")
    args = parser.parse_args()

    tier = args.tier or None
    report = run_pre_publish_gate(
        args.type,
        tier=tier,
        video_path=args.video,
        slide1=args.slide1,
        slide2=args.slide2,
        caption=args.caption,
        title=args.title,
        product=args.product,
        account_id=args.account,
    )
    print(report.summary())
    if report.warnings:
        for w in report.warnings:
            print(f"  warn: {w}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
