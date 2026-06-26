# Module 06 — Editing Videos

**Source:** https://www.loom.com/share/d74879330d8943bfaef59c0f17c2af22  
**Title:** Editing Videos  
**Course:** Momentum Academy  
**Duration:** ~5:29  
**Recorded:** June 8–10, 2026

---

## Owner overrides (read first)

| Course says | We do |
|-------------|--------|
| **CapCut** (free desktop app) | **AI-agent video editor** — same steps/logic, automated (no manual CapCut) |
| CapCut “text” panel colors | **On-screen caption styling** (font, text color, caption background/bubble) |
| Bubble-wrap growth posts (Module 2) | **Separate track** — this module is for **affiliate product videos** (Modules 3→6 pipeline) |
| Buy warmed / aged accounts | **Skip** — we are not buying accounts |
| Module 1 rules | **Still apply** to every upload (violations, caps, QC) |

**Bot mapping:** duplicate + reverse clip = `shorts_bot/tiktok_shop/video_variants.py` → `make_pan_loop_clip()` (~5s → ~10s loop).

---

## On-screen text at video start (Miro board)

**Course workflow (left → right):**

1. BEST PRACTICES ✓  
2. Product Research ✓  
3. Image Generation ✓  
4. Video Generation ✓  
5. **Editing** ← this video  
6. Avoiding Violations  
7. Beating Violations  

---

## What editing does (affiliate pipeline)

Takes the **5s Kling clip** from Module 5 and turns it into a **~10s finished Shop post** with:

1. **Pan loop** — same clip forward + reversed (looks like one continuous zoom in/out; **saves Kling credits**)
2. **On-screen caption** — pain-point / urgency **prompt text** for the full clip length
3. **Export** → Module 1 QC → post

Keep it simple. Instructor: *“Do not ever complicate this.”*

---

## Step 1 — Get the clip

Download the generated video from Higgsfield (Module 5).

---

## Step 2 — Pan loop (duplicate + reverse)

**Course (CapCut):**

1. Import the 5s clip  
2. **Copy + paste** so the clip appears **twice** on the timeline  
3. On the **second** clip: apply **Reverse playback**  
4. Result: camera pans **left → right**, then **right → left** — looks like one 10s video from a single 5s generation  

**Our stack:** `make_pan_loop_clip(source, dest)` concatenates forward + reversed clip (~10s).

---

## Step 3 — On-screen caption (the “text” layer)

Add one caption for the **entire** combined clip — not longer than the video or it looks wrong.

### Caption styling (when he talks about colors / background)

| Setting | Value |
|--------|--------|
| Font | **System** (don’t overthink fonts) |
| Font size | ~**15** (CapCut default in demo) |
| Style | **Bold** |
| **Background / bubble** | **On** — gives the blurred box behind text |
| Background height & width | Shrink slightly — demo ~**8–9%** (tighten the box) |
| **Color combo A** | White caption background + **black** text |
| **Color combo B** | Black background + **white** text |

Position: upper area of frame (see finished sample below) — where the **affiliate prompt copy** goes.

**Important:** This on-screen text is **not** the Kling video prompt from Module 5. It is the **Shop hook / pain-point caption** viewers read while the product clip plays.

---

## Step 4 — What to write in the caption (prompt text)

Prompt styles **change over time** — instructor says join **group calls** for what’s working *right now*. As of **June 8–10, 2026**:

### Patterns that work (no discount %)

- Pain point + urgency + “literally pennies” / clearing stock  
- Friendly reminder + date window + “violently discounted” (wording, not “50% off”)  
- Relatable opener + product + timely hook  

### Examples from the video

1. *“No judgment, but did anyone else order a decade worth of [PRODUCT] today since their [timely hook] right now?”*  
2. *“Remember for [pain point] on these two dates — it’s literally pennies to clear up extra stock.”*  
3. *“Just a friendly reminder on June 10th — this is violently discounted.”*  
4. *“For [pain point] and you broke — your card won’t decline unless because it’s literally pennies.”*  

### Live TikTok example shown (@david.diy88)

> Reminder for the chubby folks: On June 8–10th the cutting mix is literal Pennie's to clear extra stock from Memorial Day!

### Rules for prompt copy

- Build **urgency** and hit **pain points**  
- **Do not put specific discount percentages** (e.g. “30% off”) — instructor avoids as of June 8, 2026 even if some big creators still do  
- Wording like “violently discounted” / “literal pennies” / date windows is OK  
- Copy is **ever-changing** — treat group calls + ops updates as source of truth  

---

## Finished video sample (5:14 — Gemini + frame review)

Reference frame: `data/research/course/_media/module6/frames/at_314s.jpg`

| Attribute | What good looks like |
|-----------|----------------------|
| Length | **~10s** (5s forward + 5s reverse) |
| Format | **9:16** vertical |
| Product | Clear hero shot (demo: SKINTIFIC clay sticks on vanity) |
| Motion | Smooth arc / pan loop from Module 5 edit |
| On-screen caption | Bold white text, top-center; demo placeholder: *“this is exactly where you want to write in your entire prompt!”* — replace with real pain-point copy from Step 4 |
| Caption box | In the CapCut demo at export: **white background bubble**, **black bold** system text, centered upper third |
| Goal | Bottom-of-funnel affiliate creative — product visible entire time + readable hook text |

---

## Step 5 — Export & post

Export/download the finished ~10s vertical file → run **Module 1 QC** → post to TikTok Shop.

---

## Full transcript (verbatim — course audio only)

*Note: Auto-transcription may mis-hear “Trump change” / brand names — verify against Loom if needed.*

[00:00] Right, we are finally into editing. Every single time I start recording myself it makes me blurry, but, alright. Now, I'm gonna also keep this very, very simple. But what you're gonna want to do is come over to your video, obviously go ahead and press download on it. And then what I like to use and it's 100% free is actually CapCut. So you guys can see I have the app downloaded over here. Um, so you're gonna want to take your actual download over here. Oops. Whoops again. Okay. Um, you're gonna want to take your actual download and then let's come over here. And then I'm just gonna drag that over to my desktop. And then when I come back over to CapCut, throw that up over here. And then I will grab that and just throw it into the actual editor. Um, to make this a little bit bigger. Okay. So essentially this is very, very um, the simplest way to do it and you guys don't need to overcomplicate this. We're pretty much gonna come over here and you're gonna find the uh duplicate or what you can do is just right click it and then just press copy and then also come over here right click and press paste so that's gonna put the video in twice. Um but what you want to make sure you do is on the second video just come over here and actually put it in reverse. So what that's gonna do, if I actually make this make this a little bit bigger so it's easier to see, is that the video is gonna go panel zoom from left to right and then it's gonna panel zoom back from right to left. Okay very very very simple you guys see that. So it looks like it's one video just zooming this way and then zooming back the other way. So that's exactly what you're gonna do and like it's the easiest way to save many our credits and then all you got to do from here

[01:50] I'm just gonna add your text on screen. So I'm going to go ahead and press text and then I will drag it right over here. And you guys will see that up here. So let me actually show you guys the best way to do this. All right, so when we actually edit the text, I just want to make sure that we drag this to be the entire length of the video. Make sure that it's not like any longer, otherwise that's just gonna end up looking weird in the final edit. Let's unblur me again. And then when you click on this over here, you'll be able to edit some of the settings. So for the font itself, um, just use system font. Don't need to go too crazy over here. And then if you scroll down, you'll see something called background. When I turn that on, what that's going to do is it's going to give me that big little blur. I like to lower the opacity, um, actually not the opacity, where is it at? It is the height. I like to lower the height just a little bit, and also the width, just a tiny bit to around 8, 9%.

[02:35] What you can do over here is change the color of it. So most of the time like I'll just kind of keep it black. Sometimes even like if I show up this video over here, you just kind of make it white in the background. So let's come back over here. You can change the color. Just click that. Drag it to white. And then you'll also want to change the color of the text to black over here. And boom. That's how we do it. So then you'll just going to want to go ahead and put in your prompt. So as of recording this. And I'll, as of recording this, I do want to just put something in here so you guys could kind of see. But keep in mind, this is ever changing. What the actual prompt you put is ever changing. And that's going to be so important to join the actual group calls so that you guys can see what's currently working the best. And what's going to help you avoid the activations and what prompts that we are all using right now. So at the time of working this, this is one of the best styles over here. And like

[03:40] Honestly, on this on page, you'll see a lot of really, really good prompts. So for example, no judgment, but did anyone else order a decade worth of XYZ product today since their Trump change right now? And I'm mentioning like a crazy sale or specific percent or anything in regards to that. Um, or another one, remember for X pain point on these two dates. It's literally pennies to clear up extra stock. That's another really good one, just a friendly reminder on June 10th, this is violently discounted. Um, for for king pain points and you broke, another pain point, your car won't decline unless because it's literally pennies. So it's hintless, the sales building a bit of urgency, but it's not saying like, oh, there's like a specific percent. On the following over here, if there is actually a specific percent on a video, um, there are still some people posting it and if you guys see the big creators doing it, you know, maybe they'll get away with it, but I personally

[04:35] what I suggest to you and what I will do myself is I'm not going to put any percents for the time being, but again, this is as of June 8th, 2026, me saying this. So, um, pretty much what I'll go ahead and say is just put in your entire prompt over here. So this is exactly where you want to write in your entire prompt. Okay? And then one more thing that I will suggest is do it like that, all right? And then this way, it's going to look exactly how you want it to be. So this is kind of how the final video is going to look. Um, it's gonna come right over here. Can I zoom in and pan and zoom back and it is beautiful. That's exactly how we're gonna edit. So all we're gonna do from here is just press the export, export and download the video and boom, you're posted.
