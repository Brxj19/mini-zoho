from __future__ import annotations

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Northstar Inventory API"
    api_v1_prefix: str = "/api"
    env: str = "development"
    database_url: str = Field(
        default="mysql+pymysql://inventory_user:inventory_pass@mysql:3306/inventory_saas",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    initial_tenant_status: str = Field(default="ACTIVE", alias="INITIAL_TENANT_STATUS")
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )
    super_admin_email: str = Field(default="superadmin@example.com", alias="SUPER_ADMIN_EMAIL")
    super_admin_password: str = Field(default="ChangeMe123!", alias="SUPER_ADMIN_PASSWORD")
    super_admin_name: str = Field(default="Platform Super Admin", alias="SUPER_ADMIN_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
