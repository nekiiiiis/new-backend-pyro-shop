"""Funciones de seguridad: hashing de contraseñas y JWT.

Se usa `bcrypt` directamente (más estable que passlib en versiones recientes)
y `PyJWT` para firmar/verificar tokens HS256 con expiración.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from .config import get_settings


def hash_password(password: str) -> str:
    """Genera un hash bcrypt seguro (salt aleatorio por contraseña)."""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Comparación constant-time entre contraseña en claro y hash bcrypt."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Hash mal formado en BD
        return False


def create_access_token(payload: Dict[str, Any]) -> str:
    """Genera un JWT firmado HS256 con expiración configurable."""
    settings = get_settings()
    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    to_encode = {
        **payload,
        "iat": datetime.now(tz=timezone.utc),
        "exp": expires_at,
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodifica un JWT y devuelve su payload.

    Lanza `InvalidTokenError` o `ExpiredSignatureError` si el token no es
    válido. La capa API traduce estos errores a respuestas 401.
    """
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "InvalidTokenError",
    "ExpiredSignatureError",
]
