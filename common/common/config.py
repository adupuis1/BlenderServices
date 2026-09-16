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

settings = Settings()