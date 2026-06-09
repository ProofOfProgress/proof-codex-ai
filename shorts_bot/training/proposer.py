from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from shorts_bot.config import settings
from shorts_bot.memory.extensions import Improvement, MemoryExtensions
from shorts_bot.rewards.engine import RewardResult


class ImprovementProposer:
    """Generate self-training improvement proposals with pros and cons."""

    def __init__(
        self,
        memory: MemoryExtensions,
        client: OpenAI | None = None,
        model: str | None = None,
    ) -> None:
        self.memory = memory
        self.client = client
        self.model = model or settings.openai_model

    def propose_from_reward(self, reward: RewardResult) -> Improvement | None:
        if reward.verdict == "neutral":
            return None
        if self.client is None:
            return self._offline_proposal(reward)
        return self._llm_proposal(reward)

    def propose_from_feedback(self, topic: str, reason: str, decision: str) -> Improvement:
        title = f"Learn from {decision}: {topic[:40]}"
        if decision == "rejected":
            pros = ["Avoids repeating a pattern you vetoed", "Tightens draft quality bar"]
            cons = ["May over-correct if rejection was one-off", "Needs more approved examples to balance"]
            desc = f"When drafting similar topics, avoid: {reason}"
            cat = "drafting"
        else:
            pros = ["Reinforces what you kept", "Biases future drafts toward approved style"]
            cons = ["Could become repetitive if applied too broadly"]
            desc = f"Repeat this pattern when relevant: {reason}"
            cat = "drafting"
        return self.memory.create_improvement(
            title=title,
            category=cat,
            description=desc,
            pros=pros,
            cons=cons,
            source=f"feedback:{decision}",
        )

    def _offline_proposal(self, reward: RewardResult) -> Improvement:
        if reward.verdict == "punish":
            if "hook" in reward.diagnosis.lower() or "swipe" in reward.reason.lower():
                title = "Tighten hook and opening visual"
                cat = "hook"
                desc = "Rewrite hooks with shock/curiosity in first line; strengthen first-frame visual per course file 05."
                pros = ["Targets #1 drop-off cause on Shorts", "Fast to test on next draft"]
                cons = ["Won't fix weak core idea alone", "May feel clickbaity if overdone"]
            else:
                title = "Improve retention pacing and payoff"
                cat = "retention"
                desc = "Add progress markers, cut dead lines, land payoff earlier (course file 06)."
                pros = ["Directly addresses mid-video drop-offs", "Works with faceless voiceover format"]
                cons = ["Requires re-edit of script structure", "Takes more planning per draft"]
        else:
            title = "Double down on last video's strengths"
            cat = "strategy"
            desc = f"Analyze what worked: {reward.reason}. Reuse hook style and pacing in next Short."
            pros = ["Builds on proven signal", "Low risk incremental gain"]
            cons = ["Audience may fatigue on same formula", "Need variation to avoid sameness"]

        return self.memory.create_improvement(
            title=title,
            category=cat,
            description=desc,
            pros=pros,
            cons=cons,
            source=f"reward:{reward.verdict}:{reward.video_label}",
        )

    def _llm_proposal(self, reward: RewardResult) -> Improvement:
        applied = self.memory.applied_improvements()
        prompt = f"""Based on this YouTube Short performance result, propose ONE system improvement.

Verdict: {reward.verdict}
Score: {reward.score}
Reason: {reward.reason}
Diagnosis: {reward.diagnosis}
Metrics: {json.dumps(reward.metrics)}
Already applied improvements: {applied}

Return JSON:
- title: short title
- category: hook|retention|idea|editing|cta|strategy
- description: what to change in the bot's behavior or draft templates
- pros: list of 2-3 strings
- cons: list of 2-3 strings (honest risks)
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You improve a YouTube Shorts automation bot. Be specific. JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
        )
        data: dict[str, Any] = json.loads(response.choices[0].message.content or "{}")
        return self.memory.create_improvement(
            title=str(data.get("title", "Improvement")),
            category=str(data.get("category", "strategy")),
            description=str(data.get("description", "")),
            pros=[str(p) for p in data.get("pros", [])],
            cons=[str(c) for c in data.get("cons", [])],
            source=f"reward:{reward.verdict}:{reward.video_label}",
        )
