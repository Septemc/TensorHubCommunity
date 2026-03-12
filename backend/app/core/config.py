from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        env_prefix="TENSORHUB_",
        extra="ignore",
    )

    app_name: str = "TensorHub Community API"
    app_env: str = Field(default="development")
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/tensorhub")
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "https://tensorhub.septemc.cn"])
    uploads_dir: Path = Field(default=BASE_DIR / "uploads")
    max_upload_size_mb: int = 5
    cookie_secure: bool = False
    cookie_domain: str | None = None

    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "Admin123456!"
    bootstrap_admin_real_name: str = "TensorHub Admin"
    bootstrap_admin_email: str = "admin@tensorhub.local"
    bootstrap_admin_student_id: str = "ADMIN0001"
    bootstrap_admin_major: str = "System"
    bootstrap_admin_gender: str = "other"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    return settings
