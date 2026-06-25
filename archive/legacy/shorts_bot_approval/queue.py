from __future__ import annotations

from shorts_bot.memory.store import Draft, MemoryStore


class ApprovalQueue:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def pending(self) -> list[Draft]:
        return self.store.list_drafts(status="pending")

    def approve(self, draft_id: int, note: str = "") -> Draft:
        return self.store.review_draft(draft_id, "approved", note or "Approved.")

    def reject(self, draft_id: int, reason: str) -> Draft:
        if not reason.strip():
            raise ValueError("Rejection reason is required.")
        return self.store.review_draft(draft_id, "rejected", reason.strip())

    def format_draft(self, draft: Draft) -> str:
        return (
            f"Draft #{draft.id} [{draft.status}]\n"
            f"Topic: {draft.topic}\n"
            f"Help angle: {draft.help_angle}\n"
            f"Hook: {draft.hook}\n"
            f"Script:\n{draft.script}\n"
            f"Quality: {draft.quality_notes or 'n/a'}"
        )
