from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/shorts_bot.db")
    learned_path: Path = Path("data/LEARNED.md")
    course_dir: Path = Path("course")
    browser_profile_dir: Path = Path("data/browser_profile")
    youtube_channel_name: str = "Soft Continuity"
    channel_tagline: str = "you're still here. good."
    web_host: str = "0.0.0.0"
    web_port: int = 8080
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

    # Production — TTS voiceover (Resemble clone preferred; edge-tts fallback)
    auto_generate_voice: bool = True
    tts_provider: str = "resemble"  # resemble | edge
    resemble_api_key: str | None = None
    resemble_voice_uuid: str | None = None
    resemble_project_uuid: str | None = None
    resemble_sample_rate: int = 44100
    resemble_use_hd: bool = True
    tts_voice: str = "en-US-BrianNeural"  # edge-tts fallback only
    tts_rate: str = "-5%"
    tts_pitch: str = "+2Hz"
    visual_style: str = "ai"  # ai | stickfigure | calm_stills

    # Paid image generation (Replicate FLUX or Fal.ai)
    image_provider: str = "replicate"  # replicate | fal
    replicate_api_token: str | None = None
    replicate_image_model: str = "black-forest-labs/flux-schnell"
    fal_api_key: str | None = None
    fal_image_model: str = "fal-ai/flux/schnell"
    image_aspect_ratio: str = "9:16"
    ai_detect_max_passes: int = 5
    ai_detect_threshold: int = 35
    # Captions: ffmpeg (default) burns ASS during MP4 render; frame bakes into each PNG
    caption_mode: str = "ffmpeg"  # ffmpeg | frame
    burn_in_subtitles: bool = True  # legacy alias — True when caption_mode=ffmpeg

    # TurboScribe Whale sync (paid Unlimited — tight frame timing for A/B tests)
    use_turboscribe_sync: bool = True
    turboscribe_mode: str = "whale"
    turboscribe_always_fresh: bool = True  # re-transcribe every finish (good for testing variants)

    # Autopilot — fully AI pipeline, no human approval
    auto_approve_drafts: bool = True
    auto_upload_youtube: bool = True
    youtube_upload_visibility: str = "unlisted"

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
