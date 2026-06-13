#!/usr/bin/env python3
"""Write draft #2 beat sheet — Form 2 flicker-wave (owner review before Kling)."""

from shorts_bot.config import settings
from shorts_bot.drafts.meta import save_draft_meta
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.video_beat_sheet import (
    BeatEntry,
    format_beat_sheet_markdown,
    launch_rules_blurb,
    save_beat_sheet,
    write_beat_sheet_files,
)

HOOK = "Streetlight flickers — something too tall stands in the road and waves."
SCRIPT = (
    "Foggy rural road at night. Handheld POV never stops moving. "
    "Form 2 anomaly at the gas station — flicker-synced teleport and creepy wave. "
    "Final lunge when the light dies."
)

BEATS = [
    BeatEntry(
        0.0,
        3.5,
        "POV from driver's seat — car rolls to stop on wet two-lane road. Pine fog, abandoned gas station ahead. Headlights cut through mist.",
        camera="Handheld micro-shake inside car, then push forward out the windshield",
        audio_sfx="Engine tick, wind, low drone",
        notes="Clip 1 — establish rural dread",
    ),
    BeatEntry(
        3.5,
        7.0,
        "Step out — camera at chest height, walking toward pumps. Sodium streetlight FLICKERS orange. In the dark flash: Form 2 silhouette — too tall, wrong shoulders — at tree line.",
        camera="Forward walk, never static, slight sway",
        audio_sfx="Gravel crunch, electric flicker buzz",
        notes="Entity only visible when light dies",
    ),
    BeatEntry(
        7.0,
        10.0,
        "Light snaps OFF longer. Entity teleports one hop closer at road edge. Light ON — empty road for half a second — then shape still there, closer than before.",
        camera="Quick forward push, breath-cam wobble",
        audio_sfx="Flicker pop, footstep thud (wrong rhythm)",
        notes="End clip 1",
    ),
    BeatEntry(
        10.0,
        13.5,
        "Gas station pumps pass in foreground. Flicker rate doubles. Form 2 stands dead center between pumps — frozen while light is on.",
        camera="Orbit drift left, handheld horror movie",
        audio_sfx="Electric hum, wind gust",
        notes="Clip 2 — escalation",
    ),
    BeatEntry(
        13.5,
        17.0,
        "Entity raises one arm — slow creepy wave, wrist bent backward. Light OFF: entity jumps three meters forward in darkness. Light ON: now at pump #2, still waving.",
        camera="Push in, slight dutch tilt",
        audio_sfx="Creak, flicker, wet metal drip",
        notes="Wave is uncanny — not friendly",
    ),
    BeatEntry(
        17.0,
        20.0,
        "Camera tries to pull back — entity mirrors retreat by stepping forward each time light dies. Closer every flicker cycle.",
        camera="Backward drift, entity wins distance",
        audio_sfx="Rapid flicker bursts, breathing room tone",
        notes="End clip 2",
    ),
    BeatEntry(
        20.0,
        24.0,
        "Entity fills center frame — head too high, joints wrong. Slow wave inches from camera. Face wrong but human-ish. Flicker sync: motion ONLY in black frames.",
        camera="Locked POV but handheld tremor",
        audio_sfx="Hum drops out, single footstep",
        notes="Clip 3 — finale setup",
    ),
    BeatEntry(
        24.0,
        27.0,
        "Streetlight dies completely for two seconds. Entity lunges from arm's length to lens distance in the dark.",
        camera="Violent forward snap on light return",
        audio_sfx="Silence beat then static burst",
        notes="False calm broken",
    ),
    BeatEntry(
        27.0,
        30.0,
        "Final flicker — entity face fills frame, still mid-wave — CUT lunge with motion blur toward camera. Hard stop.",
        camera="Impact rush, horror movie sting frame",
        audio_sfx="Horror stinger + noise hit (post)",
        notes="End — no dialogue, no subtitles",
    ),
]

if __name__ == "__main__":
    store = MemoryStore(settings.database_path)
    store.update_draft_content(
        2,
        hook=HOOK,
        script=SCRIPT,
        help_angle="Form 2 flicker-wave — entity moves when streetlight dies",
    )
    save_beat_sheet(2, BEATS)
    save_draft_meta(
        2,
        visual_beats=[b.visual for b in BEATS],
        beat_sheet_approved=False,
    )
    pack = settings.data_dir / "production" / "draft_2"
    write_beat_sheet_files(
        pack,
        draft_id=2,
        topic="village eye dream worship",
        hook=HOOK,
        beats=BEATS,
        rules=launch_rules_blurb(2),
    )
    print(format_beat_sheet_markdown(
        draft_id=2,
        topic="village eye dream worship",
        hook=HOOK,
        beats=BEATS,
        rules=launch_rules_blurb(2),
    ))
