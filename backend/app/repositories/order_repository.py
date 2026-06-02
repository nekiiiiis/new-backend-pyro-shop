"""Repositorio de pedidos."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order, OrderStatus


class OrderRepository:
    """Operaciones SQL para pedidos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._db.get(Order, order_id)

    def list_all(self, status: Optional[OrderStatus] = None) -> List[Order]:
        stmt = select(Order).order_by(Order.created_at.desc())
        if status is not None:
            stmt = stmt.where(Order.status == status)
        return list(self._db.execute(stmt).scalars().all())

    def list_by_user(self, user_id: str) -> List[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def create(self, order: Order) -> Order:
        self._db.add(order)
        self._db.commit()
        self._db.refresh(order)
        return order

    def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        self._db.commit()
        self._db.refresh(order)
        return order

    def delete(self, order: Order) -> None:
        self._db.delete(order)
        self._db.commit()
