from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/shorts_bot.db")
    course_dir: Path = Path("course")
    browser_profile_dir: Path = Path("data/browser_profile")
    youtube_channel_name: str = ""
    web_host: str = "0.0.0.0"
    web_port: int = 8080
    google_client_id: str | None = None
    google_client_secret: str | None = None
    youtube_token_path: Path = Path("data/youtube_token.json")

    @property
    def has_openai(self) -> bool:
        key = (self.openai_api_key or "").strip()
        if not key:
            return False
        if "your-key" in key.lower() or key.endswith("here"):
            return False
        return True


settings = Settings()
