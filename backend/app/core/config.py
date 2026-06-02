"""Configuración tipada de la aplicación.

Las variables se leen de un archivo `.env` (cargado por pydantic-settings)
o directamente del entorno. `get_settings()` cachea la instancia para que
todos los módulos compartan la misma configuración inmutable.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración global de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Servidor
    app_env: str = Field(default="development")
    log_level: str = Field(default="info")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=3000)

    # Base de datos
    database_url: str = Field(default="sqlite:///./data/pyroshop.db")

    # Seguridad
    jwt_secret: str = Field(default="change-me-please")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expires_minutes: int = Field(default=60 * 24)

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
    )

    # Semillado inicial
    seed_on_startup: bool = Field(default=True)
    seed_admin_username: str = Field(default="admin")
    seed_admin_password: str = Field(default="123456")
    seed_user_username: str = Field(default="usuarioPrueba")
    seed_user_password: str = Field(default="123456")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve la instancia singleton de configuración."""
    return Settings()
