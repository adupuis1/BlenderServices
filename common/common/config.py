from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# common/common/config.py -> common/common -> common -> repo root, where .env lives.
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # --- Required: no default. Must be in .env (or the container's environment).
    DATABASE_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    # --- Defaults. Only put these in .env to override them.
    PROJECT_NAME: str = "Blender Services"
    API_V1_STR: str = "/api/v1"

    # LoginService: must match its own config.py exactly.
    LOGIN_SERVICE_URL: str = "http://localhost:8000"
    JWT_ISSUER: str = "http://localhost:8000"
    JWT_AUDIENCE: str = "my-apps"
    JWKS_CACHE_SECONDS: int = 3600

    # MinIO addresses as seen from your machine. Containers override the
    # internal one in compose.yml.
    S3_BUCKET: str = "blender"
    S3_INTERNAL_ENDPOINT: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT: str = "http://localhost:9000"

    # Scanning and orders.
    SCAN_TIMEOUT_SECONDS: int = 900
    PROJECT_SERVICE_URL: str = "http://localhost:8101"
    MAX_FRAMES_PER_ORDER: int = 10000
    LEASE_MINUTES: int = 30
    MAX_ATTEMPTS: int = 3


settings = Settings()