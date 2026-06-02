"""Servicio de autenticación: registro, login, JWT y cambio de contraseña."""
from __future__ import annotations

from typing import Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User, UserRole
from app.repositories import UserRepository


class AuthService:
    """Casos de uso de autenticación."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)

    @staticmethod
    def _token_for(user: User) -> str:
        return create_access_token(
            {
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
            }
        )

    def register(self, username: str, password: str) -> Tuple[User, str]:
        existing = self._users.get_by_username(username)
        if existing is not None:
            raise ConflictError("El usuario ya existe")

        user = self._users.create(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.USER,  # Política: registro público siempre crea rol 'user'.
        )
        return user, self._token_for(user)

    def login(self, username: str, password: str) -> Tuple[User, str]:
        user = self._users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            # Mensaje genérico para no filtrar si el usuario existe.
            raise AuthenticationError("Credenciales inválidas")
        return user, self._token_for(user)

    def get_current_profile(self, user_id: str) -> User:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        return user

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Contraseña actual incorrecta")
        if current_password == new_password:
            raise ValidationError("La nueva contraseña debe ser distinta de la actual")

        self._users.update_password(user, hash_password(new_password))
