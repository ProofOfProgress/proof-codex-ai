---
name: video-editor
description: Module 6 edit — pan loop plus on-screen caption burn. Attach or specify the Kling MP4 path and caption text.
---

# /video-editor

Invoke the **Video Editor** — Module 6 specialist.

Turns a **5s Kling clip** into a **~10s finished post**:

1. Pan loop (forward + reverse)
2. Burn-in pain-point caption (white box / black text)

Runs in **background** when dispatched by the main agent so other work can continue.

## Examples

```
/video-editor
Loop and caption: input data/tiktok_shop/renders/kling_raw.mp4
Caption: "Reminder for the messy desk folks — this organizer is literal pennies right now."
Output: data/tiktok_shop/renders/final.mp4

/video-editor
Edit this 5s clip with the caption from video-caption-writer
```

After edit → run `/module1-qc-runner` on the finished file before upload.

See also: `/team` · `data/research/course/VIDEO_EDITOR.md`
