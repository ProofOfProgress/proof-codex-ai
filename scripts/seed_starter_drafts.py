#!/usr/bin/env python3
"""Seed 3 on-brand starter drafts for Soft Continuity (idempotent-ish)."""

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore

STARTERS = [
    {
        "topic": "2pm energy crash",
        "hook": "You're not lazy at 2pm — your brain is paying a debt from last night.",
        "help_angle": "Helps exhausted workers fix the afternoon slump without more caffeine.",
        "script": (
            "You're not lazy at 2pm — your brain is paying a debt from last night. "
            "Before noon tomorrow: ten minutes of daylight within an hour of waking. "
            "That's it. Not a morning routine montage — one lever. "
            "This works on the days you don't believe it. You're still here. Good."
        ),
    },
    {
        "topic": "can't fall asleep",
        "hook": "If you're awake right now, don't try to sleep harder — lower the threat level.",
        "help_angle": "Helps anxious night-thinkers fall asleep with one nervous-system reset.",
        "script": (
            "If you're awake right now, don't try to sleep harder — lower the threat level. "
            "Exhale longer than you inhale. Six seconds out, three in. Do it four times. "
            "Your body can't stay in panic and sleep at once. "
            "Most people learn this too late. You don't have to."
        ),
    },
    {
        "topic": "saying no without guilt",
        "hook": "You don't need a speech to say no — you need one sentence and silence.",
        "help_angle": "Helps people-pleasers set boundaries without over-explaining.",
        "script": (
            "You don't need a speech to say no — you need one sentence and silence. "
            "Try: 'I can't take that on this week.' Full stop. No jury duty explanation. "
            "Guilt is the price of a boundary. Pay it once, not forever. "
            "You're still here. Good."
        ),
    },
]


def main() -> None:
    store = MemoryStore(settings.database_path)
    existing = {d.topic.lower() for d in store.list_drafts(limit=50)}
    created = 0
    for s in STARTERS:
        if s["topic"].lower() in existing:
            continue
        store.save_draft(
            topic=s["topic"],
            script=s["script"],
            hook=s["hook"],
            help_angle=s["help_angle"],
            quality_notes="Starter draft — Soft Continuity brand voice",
        )
        created += 1
    print(f"Seeded {created} starter draft(s). Open web UI to approve.")


if __name__ == "__main__":
    main()
