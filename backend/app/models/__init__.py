"""Modelos ORM (SQLAlchemy 2.0).

Re-exportamos las clases para que `app.models` sea el punto único de
registro de metadata en `Base`.
"""
from .order import Order, OrderItem, OrderStatus
from .product import Product, ProductCategory
from .cart import Cart, CartItem
from .user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "Product",
    "ProductCategory",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "OrderStatus",
]
