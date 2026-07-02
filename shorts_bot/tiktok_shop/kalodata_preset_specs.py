"""Course Kalodata filter presets — agent applies on hub UI (not Product Scout tool)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class KalodataUiPreset:
    key: str
    label: str
    priority: str  # P0 launch, P1, P2
    steps: list[str] = field(default_factory=list)
    notes: str = ""


# Source: module_03 transcript + coach call + hub UI screenshots (revenue 100-1k, items 50-500).
# hardcore + lurkers are SEPARATE course filters (not one combined name).
PRESETS: tuple[KalodataUiPreset, ...] = (
    KalodataUiPreset(
        key="sauce_hardcore",
        label="hardcore",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset filters first.",
            "Dates: select Yesterday.",
            "Revenue Growth Rate: set minimum to 100% or the highest growth tier available.",
            "Creator Number: maximum 200 (min none).",
            "Leave category and revenue fields empty/default unless already set.",
            "Click Submit at bottom of filter panel.",
        ],
        notes="Course 'hardcore' filter — separate from lurkers. Moe sauce tier.",
    ),
    KalodataUiPreset(
        key="sauce_lurkers",
        label="lurkers",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset filters first.",
            "Dates: Last 7 days.",
            "Creator Number: minimum 10, maximum 200.",
            "Revenue Growth Rate: minimum 10% if available.",
            "Is Affiliate Product: Yes if that checkbox exists.",
            "Click Submit.",
        ],
        notes="Course 'lurkers' filter — low saturation, products selling quietly.",
    ),
    KalodataUiPreset(
        key="sauce_hundred_gap",
        label="100 gap",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset.",
            "Dates: Yesterday.",
            "Revenue: custom range 100 to 1000 (100-1k).",
            "Item Sold: range 50 to 500.",
            "Creator Number: maximum 250.",
            "Click Submit.",
        ],
        notes="May be empty some days. Creator max 250 per owner.",
    ),
    KalodataUiPreset(
        key="sauce_hundred_gap_affiliate",
        label="100 gap + affiliate adding",
        priority="P1",
        steps=[
            "Kalodata Product page. Click Reset.",
            "Dates: Yesterday.",
            "Revenue: 100 to 1000. Item Sold: 50 to 500. Creator max 250.",
            "Revenue Source Channel: set main channel to Affiliate Adding if available.",
            "Click Submit.",
        ],
        notes="Moe custom 100 gap variant — ~5 pages of results when hot.",
    ),
    KalodataUiPreset(
        key="core_middle_core",
        label="middle core",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset.",
            "Dates: Last 7 days.",
            "Revenue Growth Rate: minimum 50%.",
            "Creator Number: maximum 200.",
            "Commission Rate: minimum 20% if filter exists.",
            "Is Affiliate Product: Yes if available.",
            "Click Submit.",
        ],
    ),
    KalodataUiPreset(
        key="core_two_hundred",
        label="200 method",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset.",
            "Dates: Yesterday.",
            "Revenue Growth Rate: minimum 100% (200% if UI allows).",
            "Creator Number: maximum 200.",
            "Click Submit.",
        ],
    ),
    KalodataUiPreset(
        key="coach_high_ticket_all",
        label="coach high ticket",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset.",
            "Dates: Last 7 days.",
            "Revenue: minimum 10000 if revenue filter allows min only.",
            "Revenue Source Content: Video if available.",
            "Revenue Growth Rate: minimum 30%.",
            "Avg Unit Price: minimum 80.",
            "Creator Number: maximum 200.",
            "Commission Rate: minimum 8%.",
            "Is Affiliate Product: Yes.",
            "Click Submit.",
        ],
    ),
    KalodataUiPreset(
        key="coach_high_ticket_furniture",
        label="coach high ticket furniture",
        priority="P0",
        steps=[
            "Kalodata Product page. Click Reset.",
            "Category: Furniture.",
            "Dates: Last 7 days.",
            "Revenue min 10000, growth min 30%, avg price min 80, creators max 200, commission min 8%.",
            "Click Submit.",
        ],
    ),
)


def preset_by_key(key: str) -> KalodataUiPreset | None:
    for p in PRESETS:
        if p.key == key:
            return p
    return None


def launch_preset_keys() -> list[str]:
    return [p.key for p in PRESETS if p.priority == "P0"]
