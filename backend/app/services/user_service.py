"""Servicio para el CRUD de usuarios (solo admin)."""
from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models import User, UserRole
from app.repositories import CartRepository, OrderRepository, UserRepository


class UserService:
    """Casos de uso administrativos sobre usuarios."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._carts = CartRepository(db)
        self._orders = OrderRepository(db)

    def list_users(self) -> List[User]:
        return self._users.list_all()

    def get_user(self, user_id: str) -> User:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        return user

    def update_role(self, *, user_id: str, role: str, requester_id: str) -> User:
        if user_id == requester_id:
            raise ValidationError("No puedes cambiar tu propio rol")

        try:
            role_enum = UserRole(role)
        except ValueError as exc:  # pragma: no cover - validado por Pydantic
            raise ValidationError("Rol inválido. Debe ser 'user' o 'admin'") from exc

        user = self.get_user(user_id)
        return self._users.update_role(user, role_enum)

    def delete_user(self, *, user_id: str, requester_id: str) -> None:
        if user_id == requester_id:
            raise ValidationError("No puedes eliminar tu propia cuenta")

        user = self.get_user(user_id)

        # Eliminar carrito y pedidos asociados antes de borrar el usuario.
        cart = self._carts.get_by_user(user_id)
        if cart is not None:
            self._db.delete(cart)

        for order in self._orders.list_by_user(user_id):
            self._db.delete(order)

        self._users.delete(user)
