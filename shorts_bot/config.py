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

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())


settings = Settings()
