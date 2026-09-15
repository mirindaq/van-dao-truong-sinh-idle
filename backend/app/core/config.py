from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vạn Đạo Trường Sinh Idle"
    database_url: str = "postgresql+asyncpg://postgres:123456@localhost:5432/mydb"
    api_cors_origins: str = Field(default="http://localhost:3000")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("database_url")
    @classmethod
    def reject_placeholder_database_host(cls, value: str) -> str:
        if "VM_IP" in value:
            raise ValueError(
                "DATABASE_URL still contains VM_IP. Replace it with your VMware PostgreSQL IP."
            )
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
