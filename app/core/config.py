from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings from env / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NextTrack"
    app_env: str = "development"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8005
    database_url: str = "sqlite:///./nexttrack.db"

    # MusicBrainz stuff — leave off unless you actually want live lookups
    musicbrainz_enabled: bool = False
    musicbrainz_base_url: str = "https://musicbrainz.org/ws/2"
    musicbrainz_user_agent: str = "NextTrack/1.0 (https://example.local/nexttrack)"
    musicbrainz_min_interval_seconds: float = 1.0
    musicbrainz_timeout_seconds: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
