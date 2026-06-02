"""Colección de routers FastAPI montados en `app/main.py`."""
from . import auth, cart, orders, products, users

__all__ = ["auth", "cart", "orders", "products", "users"]
