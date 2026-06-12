"""Black Mirror episode grammar — inject into scripts, agents, and QC."""

from __future__ import annotations

from pathlib import Path

_FORMAT_DOC = Path("channel/brand/black_mirror_format.md")


def black_mirror_format_doc_path() -> Path:
    return _FORMAT_DOC


def black_mirror_format_compact() -> str:
    """Short rules block for script + I2V prompts."""
    return """EPISODE FEEL — Black Mirror anthology (30s):
Each Short = one self-contained episode: sharp "what if" premise → normal crack → escalating consequences → twist that rewrites the hook → final sting (jumpscare) → STOP (no post-twist explanation).
Voice: clinical, precise, second-person you — not creepypasta listicle, not cosy therapy.
Twist must recontextualize line 1 (examples: you were already dead; the rule triggered before we started; the recording was the trap; the village always knew).
False calm beat before twist — in-world rationalization (glitch, lag, tired eyes, old superstition) not comedy.
Rotate settings across uploads (apartment lag, village curse-sign, warehouse pit) — same episode grammar, different mask."""


def black_mirror_script_structure() -> str:
    """Beat map for draft generator."""
    return """EPISODE BEATS (write backwards from twist + sting):
1. PREMISE (line 1): state the broken rule in one cold sentence
2. NORMAL (beats 2-3): almost believable world — one wrong detail each beat
3. ESCALATION (beats 4-5): consequences stack — time, body, witnesses, recordings fail
4. FALSE CALM (beat 6-7): quiet VO — you almost talk yourself out of it
5. TWIST (beat 7-8 spoken): one line that rewrites what the viewer assumed
6. STING (final visual + audio): jumpscare lands on the NEW truth — then cut, no denouement"""


def black_mirror_for_qc() -> str:
    return (
        "Score like a Black Mirror micro-episode: clear premise, escalating consequences, "
        "twist that recontextualizes the hook, earned finale sting — penalize random noise scares "
        "with no setup and penalize explaining the twist after the hit."
    )
