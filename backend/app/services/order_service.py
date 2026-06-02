"""Servicio de pedidos."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from app.models import Order, OrderItem, OrderStatus, UserRole
from app.repositories import CartRepository, OrderRepository, UserRepository


class OrderService:
    """Reglas de negocio para los pedidos."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._orders = OrderRepository(db)
        self._carts = CartRepository(db)
        self._users = UserRepository(db)

    def list_orders(self, status: Optional[str] = None) -> List[Order]:
        status_enum: Optional[OrderStatus] = None
        if status is not None:
            try:
                status_enum = OrderStatus(status)
            except ValueError:
                # Filtros inválidos se ignoran (compatible con backend anterior).
                status_enum = None
        return self._orders.list_all(status_enum)

    def list_my_orders(self, user_id: str) -> List[Order]:
        return self._orders.list_by_user(user_id)

    def get_order(self, *, order_id: str, requester_id: str, is_admin: bool) -> Order:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Pedido no encontrado")
        if not is_admin and order.user_id != requester_id:
            raise AuthorizationError("No autorizado para ver este pedido")
        return order

    def create_order(self, *, user_id: str) -> Order:
        cart = self._carts.get_by_user(user_id)
        if cart is None or not cart.items:
            raise ValidationError("El carrito está vacío")

        user = self._users.get_by_id(user_id)
        if user is None:
            # Caso muy raro: el usuario se borró entre el login y la operación.
            raise NotFoundError("Usuario no encontrado")

        items = [
            OrderItem(
                product_id=ci.product_id,
                nombre=ci.nombre,
                precio=ci.precio,
                cantidad=ci.cantidad,
                subtotal=round(ci.precio * ci.cantidad, 2),
            )
            for ci in cart.items
        ]
        total = round(sum(item.subtotal for item in items), 2)

        order = Order(
            user_id=user.id,
            username=user.username,
            items=items,
            total=total,
            status=OrderStatus.PENDING,
        )
        order = self._orders.create(order)

        # Vaciar carrito tras crear el pedido (mismo comportamiento que el backend anterior).
        self._carts.clear(cart)
        return order

    def update_status(self, *, order_id: str, status: str) -> Order:
        try:
            status_enum = OrderStatus(status)
        except ValueError as exc:  # pragma: no cover - validado por Pydantic
            raise ValidationError("Estado inválido. Debe ser 'pending' o 'completed'") from exc

        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Pedido no encontrado")
        return self._orders.update_status(order, status_enum)

    def cancel_order(self, *, order_id: str, requester_id: str, requester_role: str) -> None:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Pedido no encontrado")

        is_admin = requester_role == UserRole.ADMIN.value
        if not is_admin and order.user_id != requester_id:
            raise AuthorizationError("No autorizado para cancelar este pedido")
        if order.status == OrderStatus.COMPLETED:
            raise ValidationError("No se puede cancelar un pedido completado")

        self._orders.delete(order)
