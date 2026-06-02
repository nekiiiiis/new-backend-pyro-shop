"""Repositorio de carritos."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cart, CartItem


class CartRepository:
    """Operaciones SQL para carritos y sus ítems."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_user(self, user_id: str) -> Optional[Cart]:
        stmt = select(Cart).where(Cart.user_id == user_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_or_create(self, user_id: str) -> Cart:
        cart = self.get_by_user(user_id)
        if cart is None:
            cart = Cart(user_id=user_id)
            self._db.add(cart)
            self._db.commit()
            self._db.refresh(cart)
        return cart

    def save(self, cart: Cart) -> Cart:
        self._db.add(cart)
        self._db.commit()
        self._db.refresh(cart)
        return cart

    def remove_item(self, cart: Cart, product_id: str) -> Cart:
        cart.items = [item for item in cart.items if item.product_id != product_id]
        return self.save(cart)

    def clear(self, cart: Cart) -> Cart:
        cart.items = []
        return self.save(cart)

    @staticmethod
    def find_item(cart: Cart, product_id: str) -> Optional[CartItem]:
        for item in cart.items:
            if item.product_id == product_id:
                return item
        return None
