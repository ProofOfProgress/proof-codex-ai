#!/usr/bin/env bash
# Transcribe coach call audio/video → inbox markdown (Gemini).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MEDIA="${1:-}"
if [[ -z "$MEDIA" || ! -f "$MEDIA" ]]; then
  echo "Usage: bash scripts/coach_call_transcribe.sh PATH/to/recording.m4a|.mp4|.mp3" >&2
  exit 2
fi

python3 - "$MEDIA" <<'PY'
import sys
from pathlib import Path

media = Path(sys.argv[1]).resolve()
out_dir = Path("data/research/course/inbox")
out_dir.mkdir(parents=True, exist_ok=True)
stem = media.stem.replace(" ", "-")
transcript_path = out_dir / f"{stem}-transcript.md"

from shorts_bot.config import settings

key = (settings.gemini_api_key or "").strip()
if not key:
    raise SystemExit("GEMINI_API_KEY not set — cannot transcribe")

try:
    from google import genai
except ImportError:
    raise SystemExit("pip install google-genai")

client = genai.Client(api_key=key)
model = (settings.gemini_transcript_model or settings.gemini_model or "gemini-2.5-flash").strip()

uploaded = client.files.upload(file=str(media))
prompt = (
    "Transcribe this coach call recording verbatim. "
    "Use speaker labels if you can infer them (Coach, Owner). "
    "Then add sections: Product research rules, Violation/QC rules, "
    "Prompt wording, Background/visual guidance, Still-frame notes."
)
resp = client.models.generate_content(model=model, contents=[uploaded, prompt])
text = (resp.text or "").strip()

body = [
    f"# Transcript — {media.name}",
    "",
    f"Source: `{media}`",
    "",
    text,
    "",
]
transcript_path.write_text("\n".join(body), encoding="utf-8")
print(f"OK — {transcript_path}")
PY
