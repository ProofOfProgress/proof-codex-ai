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
    browser_profile_dir: Path = Path("data/browser_profile")
    browser_screenshot_dir: Path = Path("data/screenshots")
    browser_enabled: bool = True
    browser_headless: bool = True
    browser_allow_visible: bool = True
    browser_use_for_research: bool = True
    browser_save_screenshots: bool = False
    browser_open_minutes: int = 15
    youtube_channel_name: str = "Don't Blink"
    channel_series_name: str = "Don't Blink"
    channel_tagline: str = "Watch the whole thing."
    web_host: str = "127.0.0.1"
    web_port: int = 8080
    web_api_token: str | None = None  # Bearer / X-API-Token for mutating /api/* routes
    google_client_id: str | None = None
    google_client_secret: str | None = None
    youtube_token_path: Path = Path("data/youtube_token.json")

    # Discord
    discord_bot_token: str | None = None
    discord_public_key: str | None = None
    discord_owner_id: str | None = None
    discord_notify_ids: str = ""
    discord_command_prefix: str = "!"
    discord_send_briefing_on_start: bool = True
    discord_briefing_hour: int = 8
    discord_briefing_minute: int = 30
    discord_avatar_path: Path = Path("channel/brand/assets/discord_bot_avatar.png")
    discord_set_avatar_on_start: bool = False  # run avatar_cli once; avoid rate limits on every restart

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

    @field_validator("visual_style", mode="before")
    @classmethod
    def normalize_visual_style(cls, v: object) -> str:
        """Legacy VISUAL_STYLE=ai meant FLUX stills; Don't Blink launch requires I2V motion."""
        s = str(v or "ai_video").strip().lower()
        if s == "ai":
            return "ai_video"
        return s

    # Paid image generation (Replicate FLUX or Fal.ai)
    image_provider: str = "replicate"  # replicate | fal
    replicate_api_token: str | None = None
    replicate_image_model: str = "black-forest-labs/flux-schnell"
    replicate_video_model: str = "minimax/video-01"  # I2V when VISUAL_STYLE=ai_video
    ai_video_max_beats: int = 10  # cap Replicate I2V cost per Short (launch week: full beats)
    ai_video_pace_sec: float = 12.0  # delay between I2V jobs (429 guard)
    ai_video_timeout_sec: int = 600  # per-clip Replicate poll timeout
    fal_api_key: str | None = None
    fal_image_model: str = "fal-ai/flux/schnell"
    image_aspect_ratio: str = "9:16"
    ai_detect_max_passes: int = 5
    ai_detect_threshold: int = 35
    # Captions: ffmpeg (default) burns ASS during MP4 render; frame bakes into each PNG
    caption_mode: str = "ffmpeg"  # ffmpeg | frame
    burn_in_subtitles: bool = True  # legacy alias — True when caption_mode=ffmpeg

    # ffmpeg export — Shorts quality (see docs/SHORTS_ALIGNMENT.md)
    video_crf: int = 18
    video_preset: str = "slow"
    video_audio_bitrate_k: int = 192
    video_ken_burns: bool = False  # subtle zoom per segment (slower render)
    video_min_duration_seconds: float = 20.0
    video_max_duration_seconds: float = 58.0
    video_qc_blocks_upload: bool = True

    # Jumpscare audio sting — layered on final seconds of voiceover at render
    jumpscare_sting_enabled: bool = True
    jumpscare_sting_seconds: float = 2.5
    jumpscare_sting_gain: float = 2.2
    jumpscare_sting_mix: float = 0.9

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

    # YouTube — API upload only (no Studio browser automation)
    youtube_upload_via_api: bool = True
    youtube_declare_synthetic_media: bool = True  # status.containsSyntheticMedia on every upload (YouTube AI disclosure)

    # Autopilot — fully AI pipeline, no human approval
    auto_approve_drafts: bool = True
    auto_upload_youtube: bool = True
    youtube_upload_visibility: str = "public"  # owner approved auto-public (no pre-review)

    # Automation — reduce manual sync / Yes-No / publish steps (login & payments still manual)
    auto_analytics_sync: bool = True
    auto_analytics_sync_interval_hours: int = 12
    auto_approve_improvements: bool = True
    auto_approve_dev_tasks: bool = True
    # Autonomous self-training — reflective memory loop after sync + draft feedback (no LLM weight updates)
    self_training_enabled: bool = True
    self_training_promote_threshold: int = 2  # reward hits before rule → agent_memories
    auto_daily_enabled: bool = True
    auto_daily_hour: int = 11
    auto_daily_minute: int = 0
    daily_research_force_refresh: bool = True  # refresh competitor/trends each daily run
    auto_publish_hours: int = 0  # 0 = keep upload visibility (unlisted for manual review)
    quality_gate_blocks_upload: bool = True

    # YPP / inauthentic-content guard — blocks spam-farm upload patterns
    ypp_safe_mode: bool = True
    max_uploads_per_24h: int = 1
    min_hours_between_uploads: float = 20.0
    topic_cooldown_days: int = 7
    hook_cooldown_days: int = 14
    max_script_overlap_ratio: float = 0.65
    block_duplicate_draft_upload: bool = True  # same draft_id → one upload only
    block_duplicate_title_upload: bool = True  # same title already on channel → block

    # Comment automation — auto-reply light comments; serious → human queue
    auto_reply_comments: bool = True
    auto_comment_sync: bool = True
    comment_fetch_max: int = 40
    comment_max_auto_per_run: int = 8

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
    def has_resemble(self) -> bool:
        key = (self.resemble_api_key or "").strip()
        voice = (self.resemble_voice_uuid or "").strip()
        if not key or not voice:
            return False
        if "your" in key.lower() and "key" in key.lower():
            return False
        return len(key) >= 16 and len(voice) >= 8

    @property
    def has_discord(self) -> bool:
        token = (self.discord_bot_token or "").strip()
        return bool(token) and "your-bot-token" not in token.lower()

    @property
    def discord_notify_list(self) -> list[str]:
        ids = []
        if self.discord_owner_id:
            ids.append(self.discord_owner_id.strip())
        for part in (self.discord_notify_ids or "").split(","):
            p = part.strip()
            if p and p not in ids:
                ids.append(p)
        return ids


settings = Settings()
