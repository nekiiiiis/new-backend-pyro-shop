"""Dependencias FastAPI compartidas (sesión, usuario actual, admin).

Centralizar estas dependencias evita repetir la lógica de autenticación
en cada router y mantiene los controladores delgados.
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, status

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import (
    ExpiredSignatureError,
    InvalidTokenError,
    decode_access_token,
)


@dataclass(frozen=True)
class CurrentUser:
    """Información del usuario extraída del JWT."""

    id: str
    username: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def _extract_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthenticationError(
            "Acceso denegado. No se proporcionó token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    else:
        token = authorization.strip()

    if not token:
        raise AuthenticationError("Acceso denegado. No se proporcionó token.")
    return token


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    """Resuelve el usuario del header `Authorization: Bearer <token>`."""
    token = _extract_token(authorization)
    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError as exc:
        raise AuthenticationError("Token expirado.") from exc
    except InvalidTokenError as exc:
        raise AuthenticationError("Token inválido o expirado.") from exc

    user_id = payload.get("id")
    username = payload.get("username")
    role = payload.get("role")
    if not user_id or not username or not role:
        raise AuthenticationError("Token inválido o expirado.")

    return CurrentUser(id=user_id, username=username, role=role)


def get_current_admin(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Restringe el acceso a usuarios con rol admin."""
    if not current.is_admin:
        raise AuthorizationError("Acceso denegado. Se requieren permisos de administrador.")
    return current


__all__ = [
    "CurrentUser",
    "get_current_user",
    "get_current_admin",
    "get_db",
]
