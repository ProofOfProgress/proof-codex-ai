from __future__ import annotations

import re
from dataclasses import dataclass, field

from shorts_bot.course.loader import CourseKnowledgeBase, CourseFile

# Combination rules from router prompt
COMBINATIONS: dict[frozenset[str], str] = {
    frozenset({"01", "02"}): "Broad triage + idea strength",
    frozenset({"02", "03"}): "Stronger differentiated idea",
    frozenset({"02", "04"}): "Generate then evaluate ideas",
    frozenset({"02", "05"}): "Idea needs visual clarity",
    frozenset({"02", "06"}): "Good concept, weak script/payoff",
    frozenset({"03", "04"}): "Stand out in saturated space",
    frozenset({"05", "06"}): "Visual storytelling + pacing",
    frozenset({"06", "07"}): "Rewatches, comments, connection",
    frozenset({"06", "09"}): "Natural CTA integration",
    frozenset({"07", "09"}): "Community + subscriber growth",
    frozenset({"08", "06"}): "Editing/music harming retention",
}

# Trigger phrases → primary file
TRIGGERS: list[tuple[str, str]] = [
    (r"\b(help with my (content|video|channel)|why aren.t my videos|not working|broad)\b", "01"),
    (r"\b(strong enough|weak (idea|concept)|viral|hookable|compare ideas|worth making)\b", "02"),
    (r"\b(stand out|saturated|generic|positioning|blue ocean|find a lane|niche)\b", "03"),
    (r"\b(video ideas?|brainstorm|outlier|remix|original idea|what if|breakout)\b", "04"),
    (r"\b(visual|on mute|filming|first frame|props|lighting|composition)\b", "05"),
    (r"\b(script|pacing|retention|payoff|ending|rewatch|middle (is )?weak|stagnant)\b", "06"),
    (r"\b(relatable|comments?|evergreen|community|human|authentic|connection)\b", "07"),
    (r"\b(edit(ing)?|capcut|music|workflow|shortcut|over-editing|soundtrack)\b", "08"),
    (r"\b(subscriber|cta|analytics|swipe.?away|retention graph|sponsor|selling)\b", "09"),
    (r"\b(draft|hook|short)\b", "06"),
    (r"\b(idea)\b", "02"),
]


@dataclass
class RouteResult:
    primary: str
    files: list[str] = field(default_factory=list)
    main_lever: str = ""
    combination_note: str = ""

    @property
    def file_labels(self) -> list[str]:
        return self.files


class CourseRouter:
    LEVER_NAMES = {
        "01": "system triage",
        "02": "idea / hook strength",
        "03": "channel positioning",
        "04": "idea generation",
        "05": "visual / mute clarity",
        "06": "script / retention / payoff",
        "07": "engagement / relatability",
        "08": "editing / music / workflow",
        "09": "growth / CTA / analytics",
    }

    def __init__(self, kb: CourseKnowledgeBase) -> None:
        self.kb = kb

    def route(self, user_message: str) -> RouteResult:
        text = user_message.lower()
        scores: dict[str, int] = {f"{i:02d}": 0 for i in range(1, 10)}

        for pattern, file_num in TRIGGERS:
            if re.search(pattern, text, re.IGNORECASE):
                scores[file_num] += 2

        for file in self.kb.all_files():
            for anchor in file.anchors:
                if anchor in text:
                    scores[file.number] += 1

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_score = ranked[0][1] if ranked else 0
        if top_score == 0:
            primary = "01"
            selected = ["01", "02", "06"]
        else:
            primary = ranked[0][0]
            selected = [num for num, score in ranked if score > 0][:3]
            if primary not in selected:
                selected.insert(0, primary)
            if "01" not in selected and top_score <= 2:
                selected = ["01"] + selected[:2]

        selected = list(dict.fromkeys(selected))[:3]
        combo_note = ""
        key = frozenset(selected[:2])
        if key in COMBINATIONS:
            combo_note = COMBINATIONS[key]

        return RouteResult(
            primary=primary,
            files=selected,
            main_lever=self.LEVER_NAMES.get(primary, "content strategy"),
            combination_note=combo_note,
        )

    def build_guidance(self, user_message: str) -> str:
        result = self.route(user_message)
        context = self.kb.context_bundle(result.files)
        header = (
            f"ROUTED LEVER: {result.main_lever}\n"
            f"ACTIVE FILES: {', '.join(result.files)}\n"
        )
        if result.combination_note:
            header += f"COMBINATION: {result.combination_note}\n"
        free = self.kb.free_services.strip()
        free_block = f"\n\n---\n\nFREE SERVICES REFERENCE:\n{free}" if free else ""
        return f"{header}\n---\n\n{context}{free_block}"

    def failsafe_response(self) -> str:
        return "Not covered in Jenny's transcript—choose one of the covered levers and I'll help."
