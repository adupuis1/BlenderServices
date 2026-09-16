from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    PROJECT_NAME: str = "Blender Services"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://blender:dev@localhost:5433/blender"


    LOGIN_SERVICE_URL: str = "http://backend:8000"
    JWT_ISSUER: str = "http://localhost:8000"
    JWT_AUDIENCE: str = "my-apps"
    JWKS_CACHE_SECONDS: int = 3600


    
    # MinIO. You invent the key and secret; see 2.3.
    S3_ACCESS_KEY: str = "blenderadmin"
    S3_SECRET_KEY: str = "change_me_min_8_chars"
    S3_BUCKET: str = "blender"
    S3_INTERNAL_ENDPOINT: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT: str = "http://localhost:9000"

    # scanning.
    SCAN_TIMEOUT_SECONDS: int = 900

    # orderService.
    PROJECT_SERVICE_URL: str = "http://localhost:8101"
    MAX_FRAMES_PER_ORDER: int = 10000
    LEASE_MINUTES: int = 30
    MAX_ATTEMPTS: int = 3
settings = Settings()