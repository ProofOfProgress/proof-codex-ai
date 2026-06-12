"""Industrial death-metal aesthetic for Peripheral — theatrical ritual, YPP-safe."""

from __future__ import annotations

from pathlib import Path

_METAL_DOC = Path("channel/brand/metal_aesthetic.md")

# Script / metadata phrases that imply real animal harm — block before upload
ANIMAL_HARM_SCRIPT_MARKERS = (
    "eating the bird",
    "ate the bird",
    "chewing the head",
    "bit off the",
    "devoured the",
    "tore off the beak",
    "live chicken",
    "live bird",
    "animal cruelty",
)

# Visual prompt tokens that tend to produce YPP / age-restricted frames
ANIMAL_HARM_VISUAL_MARKERS = (
    "eating bird",
    "chewing flesh",
    "live bird",
    "dead bird",
    "animal slaughter",
    "blood splatter",
    "open wound",
    "dismember",
)


def metal_aesthetic_compact() -> str:
    """Inject into script + I2V prompts."""
    return """METAL AESTHETIC (Peripheral — Slipknot-adjacent theatre, NOT snuff):
Energy: industrial death-metal / nu-metal — numbered metal masks, black jumpsuit, chains, warehouse pit, red strobe, fog.
Ritual symbolism: porcelain beak mask, feathers on collar/stage, empty cage, ritual plate with feathers only.
NEVER on screen: live birds harmed, eating/chewing flesh, animal cruelty, open wounds, blood spray, step-by-step harm.
Scare grammar: off-screen crunch or chant drop → cut to aftermath (empty circle, dropped mask, feathers on concrete).
Merch crossover: biker leather + PERIPH eye patch energy — sacred eye × street raw.
YPP: stay advertiser-friendly — implied dread only; volume warning on hard finales."""


def ypp_safe_ritual_rules() -> str:
    """Short block for QC + draft repair."""
    return (
        "YPP RITUAL RULE: bird/offering imagery must be SYMBOLIC — masks, feathers, empty cage. "
        "No live animals, no eating on camera, no graphic gore. Cut before the act; show aftermath only."
    )


def metal_visual_fragment() -> str:
    """I2V / still prompt suffix."""
    return (
        "Industrial metal horror theatre: masked figures in black jumpsuits, chain texture, "
        "warehouse concrete, red strobe spill, feather props on floor or mask collar — "
        "no live birds, no flesh, no gore spray, photoreal cinematic grain."
    )


def metal_negative_prompt_extra() -> str:
    return (
        "live bird, dead bird, animal cruelty, eating flesh, chewing, slaughter, "
        "graphic blood spray, open wounds, dismemberment, real animal harm, snuff"
    )


def script_animal_harm_issues(*parts: str) -> list[str]:
    blob = " ".join(p for p in parts if p).lower()
    return [f"YPP animal-harm language: {m!r}" for m in ANIMAL_HARM_SCRIPT_MARKERS if m in blob]


def visual_prompt_animal_harm_issues(prompt: str) -> list[str]:
    lower = (prompt or "").lower()
    return [f"YPP visual risk: {m!r}" for m in ANIMAL_HARM_VISUAL_MARKERS if m in lower]


def metal_doc_summary() -> str:
    if _METAL_DOC.exists():
        return _METAL_DOC.read_text(encoding="utf-8").strip()[:1400]
    return metal_aesthetic_compact()
