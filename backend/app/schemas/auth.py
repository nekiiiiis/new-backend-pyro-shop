"""Esquemas Pydantic para autenticación."""
from __future__ import annotations

from pydantic import BaseModel, Field

from .user import UserSummary


class RegisterCredentials(BaseModel):
    """Validación estricta para creación de usuarios."""

    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class LoginCredentials(BaseModel):
    """Login: solo exige presencia (las reglas estrictas aplican al registro)."""

    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    """Respuesta de login/registro: token + datos básicos del usuario."""

    message: str
    token: str
    user: UserSummary


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=6, max_length=128, alias="currentPassword")
    new_password: str = Field(min_length=6, max_length=128, alias="newPassword")

    model_config = {
        "populate_by_name": True,
    }
