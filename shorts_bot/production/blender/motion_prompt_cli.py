"""CLI — describe motion in English → JSON keyframes for Blender."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.blender.motion_prompt import (
    generate_motion_keyframes,
    load_beat_prompt,
    prepare_motion_for_pack,
    resolve_backend,
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Natural-language motion → Blender pose keys")
    parser.add_argument("--draft-id", type=int, default=2)
    parser.add_argument("--phase", choices=("open", "wave", "lunge"), default="wave")
    parser.add_argument("--prompt", type=str, default=None, help="Override beat sheet text")
    parser.add_argument("--pack-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--all-phases", action="store_true", help="Generate open+wave+lunge")
    args = parser.parse_args(argv)

    pack = args.pack_dir or settings.data_dir / "production" / f"draft_{args.draft_id}"
    backend = resolve_backend()
    print(f"Motion backend: {backend}")

    if args.all_phases:
        paths = prepare_motion_for_pack(pack, args.draft_id, force=args.force, prompt_override=args.prompt)
        for phase, path in paths.items():
            print(f"  {phase}: {path}")
        return

    prompt = args.prompt or load_beat_prompt(args.draft_id, args.phase)
    print(f"Prompt ({args.phase}): {prompt[:120]}…" if len(prompt) > 120 else f"Prompt ({args.phase}): {prompt}")
    payload = generate_motion_keyframes(prompt, phase=args.phase)
    out = pack / f"motion_{args.phase}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({payload['backend']}, {len(payload['keyframes'])} keyframes)")


if __name__ == "__main__":
    main()
