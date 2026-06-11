"""YouTube comment triage — auto-reply light comments, queue serious ones."""

from shorts_bot.comments.runner import CommentRunResult, run_comment_automation

__all__ = ["CommentRunResult", "run_comment_automation"]
