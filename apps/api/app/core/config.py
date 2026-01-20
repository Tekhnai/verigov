from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_access_minutes: int = Field(default=15, alias="JWT_ACCESS_MINUTES")
    jwt_refresh_days: int = Field(default=7, alias="JWT_REFRESH_DAYS")
    cors_origins: str = Field(default="", alias="CORS_ORIGINS")
    use_mock_connectors: bool = Field(default=True, alias="USE_MOCK_CONNECTORS")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")
    cnpj_cache_ttl_seconds: int = Field(default=86400, alias="CNPJ_CACHE_TTL_SECONDS")

    def cors_origin_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
