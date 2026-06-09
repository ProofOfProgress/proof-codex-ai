from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
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

    @property
    def has_openai(self) -> bool:
        key = (self.openai_api_key or "").strip()
        if not key:
            return False
        if "your-key" in key.lower() or key.endswith("here"):
            return False
        return True

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
