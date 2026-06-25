"""Default analytics ritual — review last uploads (good + bad metrics)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VideoAnalyticsReview:
    video_label: str
    title: str
    views: int
    avg_watch_pct: float | None
    likes: int
    comments: int
    swipe_pct: float | None
    swipe_source: str
    verdict: str  # good | mixed | bad
    goods: list[str] = field(default_factory=list)
    bads: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class LastUploadsReview:
    videos: list[VideoAnalyticsReview]
    summary: str
    synced: bool

    def to_text(self) -> str:
        lines = [self.summary, ""]
        for v in self.videos:
            lines.append(f"## {v.title[:70]}")
            lines.append(f"Views: {v.views} · Avg watch: {v.avg_watch_pct or 0:.0f}% · Verdict: {v.verdict}")
            if v.goods:
                lines.append("Good:")
                lines.extend(f"  + {g}" for g in v.goods)
            if v.bads:
                lines.append("Bad:")
                lines.extend(f"  − {b}" for b in v.bads)
            if v.notes:
                lines.extend(f"  · {n}" for n in v.notes)
            lines.append("")
        return "\n".join(lines).strip()


def _review_one(row: dict) -> VideoAnalyticsReview:
    m = row.get("metrics") or {}
    title = str(m.get("title") or row.get("video_label") or "Unknown")
    label = str(row.get("video_label") or title)
    views = int(m.get("views") or 0)
    likes = int(m.get("likes") or 0)
    comments = int(m.get("comments") or 0)
    avg_raw = m.get("average_view_percentage", m.get("retention_rate"))
    avg = float(avg_raw) if avg_raw not in (None, "") else None
    swipe_raw = m.get("viewed_vs_swiped_away")
    swipe = float(swipe_raw) if swipe_raw not in (None, "") else None
    swipe_src = str(m.get("swipe_source") or "unavailable")

    goods: list[str] = []
    bads: list[str] = []
    notes: list[str] = []

    if avg is not None:
        if avg >= 60:
            goods.append(f"Strong avg watch ({avg:.0f}%) — people stayed")
        elif avg >= 50:
            goods.append(f"Decent avg watch ({avg:.0f}%)")
        elif avg < 45:
            bads.append(f"Low avg watch ({avg:.0f}%) — hook or payoff likely weak")
        else:
            notes.append(f"Mid avg watch ({avg:.0f}%) — check Studio retention graph")

    if views >= 500:
        goods.append(f"Solid reach ({views:,} views in API window)")
    elif views >= 100:
        notes.append(f"Moderate views ({views}) — early or niche audience")
    elif views > 0:
        bads.append(f"Low views ({views}) — distribution or hook may need work")
    else:
        bads.append("No views in window — just uploaded or not indexed yet")

    if likes >= max(views // 20, 3):
        goods.append(f"Engagement: {likes} likes")
    elif views >= 50 and likes == 0:
        bads.append("Zero likes despite views — weak emotional pull or CTA")

    if comments >= 2:
        goods.append(f"{comments} comments — conversation started")
    elif views >= 200 and comments == 0:
        notes.append("No comments yet — comment CTA may be too soft")

    if swipe is not None:
        if swipe >= 70:
            goods.append(f"High viewed-vs-swipe ({swipe:.0f}%) — hook wins feed")
        elif swipe < 50:
            bads.append(f"High swipe-away ({100 - swipe:.0f}% skipped) — fix first 2 seconds")
    else:
        notes.append("Swipe-away N/A — paste from YouTube Studio via /api/score for hook truth")

    if avg is not None and avg >= 55 and views >= 100:
        verdict = "good"
    elif bads and not goods:
        verdict = "bad"
    elif bads and goods:
        verdict = "mixed"
    elif avg is not None and avg < 45:
        verdict = "bad"
    else:
        verdict = "mixed"

    return VideoAnalyticsReview(
        video_label=label,
        title=title,
        views=views,
        avg_watch_pct=avg,
        likes=likes,
        comments=comments,
        swipe_pct=swipe,
        swipe_source=swipe_src,
        verdict=verdict,
        goods=goods,
        bads=bads,
        notes=notes,
    )


def review_last_uploads(
    *,
    limit: int = 5,
    sync: bool = True,
    days: int = 28,
) -> LastUploadsReview:
    """
    Owner default: unless told otherwise, check last uploads — good and bad metrics.
    """
    from shorts_bot.config import settings
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore

    mem = MemoryExtensions(MemoryStore(settings.database_path))
    synced = False

    if sync:
        from shorts_bot.training.proposer import ImprovementProposer
        from shorts_bot.youtube.sync import AnalyticsSync

        AnalyticsSync(mem, ImprovementProposer(mem)).run(days=days)
        synced = True

    rows = mem.list_analytics(limit=limit)
    if not rows:
        return LastUploadsReview(
            videos=[],
            summary="No analytics stored yet. Upload a Short, then run analytics review with --sync.",
            synced=synced,
        )

    reviews = [_review_one(r) for r in rows[:limit]]
    good_n = sum(1 for v in reviews if v.verdict == "good")
    bad_n = sum(1 for v in reviews if v.verdict == "bad")
    mixed_n = len(reviews) - good_n - bad_n
    summary = (
        f"Last {len(reviews)} upload(s): {good_n} good, {mixed_n} mixed, {bad_n} need work. "
        "Avg watch % is from YouTube API (28d window) — not the Studio retention graph. "
        "Swipe-away requires Studio paste."
    )
    return LastUploadsReview(videos=reviews, summary=summary, synced=synced)
