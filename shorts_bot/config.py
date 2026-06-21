from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"

    # Chief Manager + specialist workers (Gemini) — primary chat path when duration/prefix set
    manager_display_name: str = "AlphaBeta001"  # agent name (not the YouTube channel)
    manager_enabled: bool = True
    manager_work_floor_seconds: int = 30
    manager_max_work_seconds: int = 7200  # cap 2h work budgets
    manager_async_threshold_seconds: int = 120  # web: background job if budget exceeds this
    manager_work_priority: str = "research"  # research | balanced | production
    manager_auto_delegate: bool = True  # route research/plan messages to manager (not underlings)
    manager_default_research_seconds: int = 180  # auto burst when priority=research, no duration given
    manager_research_force_refresh: bool = False  # underlings re-fetch web on deep research
    data_dir: Path = Path("data")
    database_path: Path = Path("data/shorts_bot.db")
    learned_path: Path = Path("data/LEARNED.md")
    memory_markdown_path: Path = Path("data/MEMORY.md")
    memory_chat_context_limit: int = 24

    # Deep research — web browse + vidIQ + YouTube competitors
    research_web_enabled: bool = True
    research_max_web_snippets: int = 8
    tavily_api_key: str | None = None
    vidiq_enabled: bool = False  # off by default — browser + Trends + YouTube API instead
    vidiq_api_key: str | None = None  # vidIQ Max MCP API key → mcp.vidiq.com
    vidiq_use_browser: bool = True
    google_trends_enabled: bool = True
    google_trends_geo: str = "US"
    google_trends_gprop: str = "youtube"  # youtube | web | news | images | froogle
    google_trends_timeframe: str = "today 3-m"
    research_cache_days: int = 7  # 0 = never expire cached deep research
    course_dir: Path = Path("course")
    # Codex search + ask (BM25 over markdown; Gemini answers when key set)
    codex_search_max_chunks: int = 8
    codex_max_context_chars: int = 12000
    browser_profile_dir: Path = Path("data/browser_profile")
    browser_screenshot_dir: Path = Path("data/screenshots")
    browser_enabled: bool = True
    browser_headless: bool = True
    browser_allow_visible: bool = True
    browser_use_for_research: bool = True
    browser_save_screenshots: bool = False
    browser_open_minutes: int = 15
    youtube_channel_name: str = "Peripheral"
    channel_series_name: str = "Peripheral"
    channel_tagline: str = "Watch the whole thing."
    web_host: str = "127.0.0.1"
    web_port: int = 8080
    web_api_token: str | None = None  # Bearer / X-API-Token for mutating /api/* routes

    # Slack — bot token (AlphaBeta001 app) and/or webhook; @cursor is separate (Cursor OAuth)
    slack_bot_token: str | None = None  # xoxb-... from api.slack.com custom app
    slack_channel_id: str | None = None  # C... for chat.postMessage
    slack_webhook_url: str | None = None
    slack_notify_enabled: bool = True
    slack_channel_name: str = "peripheral-ops"
    slack_bot_display_name: str = "AlphaBeta001"
    slack_cursor_linked: bool = False  # set true after @cursor Link Account in Slack
    slack_app_token: str | None = None  # xapp-... Socket Mode (autonomy bus)
    slack_autonomy_enabled: bool = True  # [autonomy] self-talk bus via Socket Mode
    slack_autonomy_owner_commands: bool = False  # also run plain human messages (no prefix)
    slack_channel_email: str | None = None  # peripheral-ops@workspace.slack.com (Option A)
    gmail_smtp_user: str | None = None  # sender Gmail for Slack email + alerts
    gmail_smtp_app_password: str | None = None  # Google App Password (not login password)
    slack_post_mode: str = "auto"  # auto | email | bot — auto tries bot, webhook, then email
    google_client_id: str | None = None
    google_client_secret: str | None = None
    youtube_token_path: Path = Path("data/youtube_token.json")

    # TikTok Content Posting API
    tiktok_client_key: str | None = None
    tiktok_client_secret: str | None = None
    tiktok_token_path: Path = Path("data/tiktok_token.json")
    tiktok_redirect_uri: str = "http://127.0.0.1:8091/"
    tiktok_oauth_scopes: str = "user.info.basic,video.publish"
    tiktok_privacy_level: str = ""  # empty = auto-pick from creator_info
    tiktok_declare_aigc: bool = True
    tiktok_disable_duet: bool = False
    tiktok_disable_stitch: bool = False
    tiktok_disable_comment: bool = False
    auto_upload_tiktok: bool = False

    # InVideo AI — MCP + browser production
    invideo_api_key: str | None = None
    invideo_mcp_url: str = "https://mcp.invideo.io/mcp"
    invideo_app_url: str = "https://ai.invideo.io"
    invideo_default_platform: str = "youtube_shorts"
    invideo_default_vibe: str = "professional"
    invideo_default_audience: str = "AI curious adults"
    invideo_twin_enabled: bool = True
    invideo_copilot_url: str = ""  # saved workspace .../v40-copilot URL

    # Paid production stack — Resemble + AssemblyAI transcript + Gemini vision QC
    require_paid_stack: bool = True
    allow_free_tts_fallback: bool = False  # edge-tts only when True + Resemble missing
    resemble_fallback_on_429: bool = True  # edge horror pacing when Resemble rate-limits
    allow_script_timing_fallback: bool = False  # script WPS only when True + transcript API fails

    # Production — TTS voiceover (Resemble clone; edge-tts emergency fallback only)
    auto_generate_voice: bool = True
    tts_provider: str = "resemble"  # resemble | edge
    resemble_api_key: str | None = None
    resemble_voice_uuid: str | None = None
    resemble_project_uuid: str | None = None
    resemble_sample_rate: int = 44100
    resemble_use_hd: bool = True
    tts_voice: str = "en-US-AndrewNeural"  # edge-tts fallback — deep horror narrator
    tts_rate: str = "-12%"
    tts_pitch: str = "-4Hz"
    tts_horror_delivery: bool = True  # SSML dread pacing for Don't Blink scripts
    resemble_horror_prompt: str = ""  # empty = built-in horror delivery primer
    visual_style: str = "ai_video"  # ai_video (I2V clips) | hybrid | ai (legacy → ai_video)
    # Content format — see shorts_bot/production/content_format.py + docs/CONTENT_FORMATS.md
    content_format: str = "short_30"  # short_30 | short_hybrid | long_compilation | long_still | long_hybrid

    @field_validator("visual_style", mode="before")
    @classmethod
    def normalize_visual_style(cls, v: object) -> str:
        """Legacy VISUAL_STYLE=ai meant FLUX stills; Don't Blink launch requires I2V motion."""
        s = str(v or "ai_video").strip().lower()
        if s == "ai":
            return "ai_video"
        return s

    # Paid AI video generation (Replicate I2V / FLUX stills) — off unless owner opts in
    ai_video_generation_enabled: bool = False

    # Paid image generation (Replicate FLUX or Fal.ai)
    image_provider: str = "replicate"  # replicate | fal
    replicate_api_token: str | None = None
    replicate_image_model: str = "black-forest-labs/flux-schnell"
    # Video backend — blender (local EEVEE 3D) | kling (API) | legacy_i2v (MiniMax/Hailuo)
    video_backend: str = "blender"
    kling_provider: str = "official"  # official | replicate | fal
    kling_access_key: str | None = None
    kling_secret_key: str | None = None
    kling_model: str = "kling-v2-6"  # official API model_name; replicate uses kwaivgi/kling-v3-video
    kling_clip_seconds: int = 10  # official v2.6 API: 5 or 10; use 10 for longer beats
    kling_clips_per_short: int = 3  # 3×10s ≈ 30s Short (one stitch between clips)
    kling_generate_audio: bool = True  # lip-sync dialogue + ambient in one pass
    kling_skip_narrator_tts: bool = True  # no Resemble when Kling carries voices
    kling_mode: str = "std"  # std=720p | pro=1080p
    kling_aspect_ratio: str = "9:16"
    kling_multi_shot: bool = True  # multi_prompt inside each clip
    kling_force_regen: bool = False  # ignore cached kling_part_*.mp4
    # Blender 3D — local EEVEE renders (no API credits)
    blender_clips_per_short: int = 3
    blender_clip_seconds: float = 10.0
    blender_samples: int = 32  # EEVEE TAA samples — lower = faster cloud renders
    blender_force_regen: bool = False
    replicate_video_model: str = "minimax/video-01"  # legacy I2V default
    replicate_video_model_hook: str = "minimax/video-01"
    replicate_video_model_jumpscare: str = "minimax/hailuo-2.3-fast"
    jumpscare_dedicated_clip: bool = True  # finale = setup hold + short Hailuo lunge (not slideshow zoom)
    screen_text_overlay_enabled: bool = True  # composited CCTV / alarm-clock UI (not AI-generated glyphs)
    screen_text_phone_enabled: bool = False  # no phone screens — fullscreen CCTV + alarm clock for time
    screen_text_screen_only: bool = True  # legacy phone rect mode (off while screen_text_phone_enabled=false)
    screen_text_draw_phone_ui: bool = True  # ignored when screen_text_phone_enabled=false
    jumpscare_auto_generate: bool = False  # requires ai_video_generation_enabled + existing clip preferred
    jumpscare_clip_play_seconds: float = 2.85  # how long the scare motion plays in the final Short
    jumpscare_i2v_tail_seconds: float = 2.4  # extract lunge from end of Hailuo output
    jumpscare_setup_min_seconds: float = 0.55  # min pre-scare hold — tighter lunge sync with VO
    jumpscare_visual_flash: bool = True  # ffmpeg zoom+flash when dedicated clip is off
    ai_video_max_beats: int = 2  # Kling lock-in: 2 clips; legacy_i2v may raise to 10
    ai_video_pace_sec: float = 12.0  # delay between I2V jobs (429 guard)
    ai_video_timeout_sec: int = 600  # per-clip Replicate poll timeout
    fal_api_key: str | None = None
    fal_image_model: str = "fal-ai/flux/schnell"
    image_aspect_ratio: str = "9:16"
    ai_detect_max_passes: int = 10
    ai_detect_threshold: int = 5  # 0–100 heuristic; target ≤5 ≈ under 5% AI likelihood
    ai_detect_blocks_render: bool = True
    # Captions: ffmpeg (default) burns ASS during MP4 render; frame bakes into each PNG
    caption_mode: str = "ffmpeg"  # ffmpeg | frame
    burn_in_subtitles: bool = True  # legacy alias — True when caption_mode=ffmpeg

    # ffmpeg export — Shorts quality (see docs/SHORTS_ALIGNMENT.md)
    video_crf: int = 16
    video_preset: str = "slow"
    video_audio_bitrate_k: int = 192
    video_ken_burns: bool = False  # subtle zoom per segment (slower render)
    video_min_duration_seconds: float = 20.0
    video_max_duration_seconds: float = 58.0
    video_qc_blocks_upload: bool = True

    # Horror SFX — agent-mixed procedural cues + finale stinger at render (replaces raw noise sting)
    horror_sfx_enabled: bool = True
    # Legacy white-noise sting (off when horror_sfx_enabled)
    jumpscare_sting_enabled: bool = False
    jumpscare_sting_seconds: float = 2.5
    jumpscare_sting_gain: float = 2.2
    jumpscare_sting_mix: float = 0.9
    # Unlisted QA uploads skip 24h cooldown (owner preview / SFX validation)
    unlisted_qa_bypass_upload_cooldown: bool = False  # YPP: unlisted QA uploads count toward 24h cap

    # Gemini vision QC — sparse frames, one batched call (see vision_qc.py)
    vision_qc_enabled: bool = True
    vision_qc_blocks_upload: bool = True
    vision_qc_min_score: float = 7.5  # launch bar — bump to 8.0 for first uploads if needed
    vision_qc_max_frames: int = 5
    vision_qc_frame_width: int = 360
    vision_qc_jpeg_quality: int = 72
    gemini_vision_model: str = ""  # empty = use gemini_model (flash-lite)

    # Production variety — rotate visual/caption/motion axes per draft (YPP anti-fingerprint)
    production_variety_enabled: bool = True

    # Quality gates — block before expensive steps / upload
    quality_gate_blocks_render: bool = True

    # Transcript sync — Gemini audio (default; uses GEMINI_API_KEY). AssemblyAI optional fallback.
    transcript_provider: str = "gemini"  # gemini | assemblyai
    gemini_transcript_model: str = ""  # empty = gemini_model
    assemblyai_api_key: str | None = None  # optional — only if transcript_provider=assemblyai
    assemblyai_speech_model: str = "universal"
    transcript_always_fresh: bool = False  # reuse transcript.txt on pipeline retry (saves API $)

    # YouTube — API upload preferred; Studio browser fallback when OAuth missing on VM
    youtube_upload_via_api: bool = True
    youtube_studio_upload_fallback: bool = True
    youtube_declare_synthetic_media: bool = True  # status.containsSyntheticMedia on every upload (YouTube AI disclosure)
    youtube_category_id: str = "24"  # Entertainment — horror Shorts (not 22 self-help)
    post_upload_cta_comment: bool = True  # series engagement comment after API upload
    post_upload_analytics_sync: bool = True
    launch_quality_strict: bool = True  # false-calm missing = quality issue, not warning
    launch_silent_video_count: int = 3  # first N Shorts: no talking, no subtitles; SFX/ambient OK
    require_beat_sheet_before_video: bool = True  # write VIDEO_BEAT_SHEET.md before Kling
    require_beat_sheet_approval: bool = True  # block Kling/upload until owner approves beat sheet
    pipeline_exclusive_lock: bool = True  # one finish_cli / Replicate job at a time
    pipeline_auto_horror_repair: bool = True  # fix first-person drift before TTS/I2V
    pipeline_block_voice_drift: bool = True  # re-check after humanize; repair or fail

    # Autopilot — YPP-safe defaults: human review before public monetized uploads
    auto_approve_drafts: bool = False
    auto_upload_youtube: bool = False
    youtube_upload_visibility: str = "unlisted"  # public only after manual Studio review

    # Automation — reduce manual sync / Yes-No / publish steps (login & payments still manual)
    auto_analytics_sync: bool = True
    auto_analytics_sync_interval_hours: int = 12
    auto_approve_improvements: bool = True
    auto_approve_dev_tasks: bool = True
    # Autonomous self-training — reflective memory loop after sync + draft feedback (no LLM weight updates)
    self_training_enabled: bool = True
    self_training_promote_threshold: int = 2  # reward hits before rule → agent_memories
    workflow_evolution_enabled: bool = True  # daily loop steps/params evolve from runs + analytics
    auto_daily_enabled: bool = False  # enable only with human upload approval workflow
    auto_daily_hour: int = 11
    auto_daily_minute: int = 0
    pipeline_backend: str = "invideo"  # invideo | legacy (homemade render — retired)
    daily_research_force_refresh: bool = True  # refresh competitor/trends each daily run
    auto_publish_hours: int = 0  # 0 = keep upload visibility (unlisted for manual review)
    quality_gate_blocks_upload: bool = True

    # YPP / inauthentic-content guard — blocks spam-farm upload patterns
    ypp_safe_mode: bool = True
    max_uploads_per_24h: int = 1
    min_hours_between_uploads: float = 20.0
    upload_guard_void_video_ids: list[str] = ["JIkMhPH0l6o"]  # erroneous non-horror upload
    topic_cooldown_days: int = 7
    hook_cooldown_days: int = 14
    max_script_overlap_ratio: float = 0.50
    ypp_allow_batch_series_upload: bool = False  # upload_series_cli — banned for monetized channels
    ypp_block_qa_iteration_titles: bool = True  # block titles like "(build v9 ...)"
    block_duplicate_draft_upload: bool = True  # same draft_id → one upload only
    block_duplicate_title_upload: bool = True  # same title already on channel → block

    # Comment automation — auto-reply light comments; serious → human queue
    auto_reply_comments: bool = True
    auto_comment_sync: bool = True
    comment_fetch_max: int = 40
    comment_max_auto_per_run: int = 3  # scale auto-replies = inauthentic engagement signal

    @property
    def has_openai(self) -> bool:
        key = (self.openai_api_key or "").strip()
        if not key:
            return False
        if "your-key" in key.lower() or key.endswith("here"):
            return False
        return True

    @property
    def has_gemini(self) -> bool:
        key = (self.gemini_api_key or "").strip()
        if not key:
            return False
        lower = key.lower()
        if "your_api_key" in lower or "your-key" in lower or key.endswith("here"):
            return False
        return len(key) >= 20

    @property
    def has_full_chat(self) -> bool:
        return self.has_gemini or self.has_openai

    @property
    def chat_provider(self) -> str:
        if self.has_gemini:
            return "gemini"
        if self.has_openai:
            return "openai"
        return "offline"

    @property
    def has_replicate_images(self) -> bool:
        token = (self.replicate_api_token or "").strip()
        return bool(token) and len(token) >= 8 and "your" not in token.lower()

    @property
    def has_fal_images(self) -> bool:
        key = (self.fal_api_key or "").strip()
        return bool(key) and len(key) >= 8 and "your" not in key.lower()

    @property
    def has_paid_images(self) -> bool:
        return self.has_replicate_images or self.has_fal_images

    @property
    def has_assemblyai(self) -> bool:
        key = (self.assemblyai_api_key or "").strip()
        if not key:
            return False
        if "your" in key.lower() and "key" in key.lower():
            return False
        return len(key) >= 16

    @property
    def has_kling_official(self) -> bool:
        ak = (self.kling_access_key or "").strip()
        sk = (self.kling_secret_key or "").strip()
        return len(ak) >= 8 and len(sk) >= 8 and "your" not in ak.lower()

    @property
    def uses_kling_video(self) -> bool:
        return (self.video_backend or "").strip().lower() == "kling"

    @property
    def uses_blender_video(self) -> bool:
        return (self.video_backend or "").strip().lower() == "blender"

    @property
    def uses_kling_native_audio(self) -> bool:
        return (
            self.uses_kling_video
            and bool(self.kling_generate_audio)
            and bool(self.kling_skip_narrator_tts)
        )

    @property
    def has_resemble(self) -> bool:
        key = (self.resemble_api_key or "").strip()
        voice = (self.resemble_voice_uuid or "").strip()
        if not key or not voice:
            return False
        if "your" in key.lower() and "key" in key.lower():
            return False
        return len(key) >= 16 and len(voice) >= 8

settings = Settings()
