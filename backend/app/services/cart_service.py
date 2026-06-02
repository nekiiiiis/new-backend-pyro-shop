"""Servicio del carrito: añadir, actualizar, eliminar y vaciar."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models import Cart, CartItem
from app.repositories import CartRepository, ProductRepository


class CartService:
    """Reglas de negocio del carrito."""

    MAX_QUANTITY = 999

    def __init__(self, db: Session) -> None:
        self._db = db
        self._carts = CartRepository(db)
        self._products = ProductRepository(db)

    def get_cart(self, user_id: str) -> Cart:
        return self._carts.get_or_create(user_id)

    def add_item(self, *, user_id: str, product_id: str, cantidad: int) -> Cart:
        if cantidad < 1 or cantidad > self.MAX_QUANTITY:
            raise ValidationError(f"La cantidad debe estar entre 1 y {self.MAX_QUANTITY}")

        product = self._products.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Producto no encontrado")

        cart = self._carts.get_or_create(user_id)
        existing = self._carts.find_item(cart, product_id)

        if existing is not None:
            new_quantity = existing.cantidad + cantidad
            if new_quantity > self.MAX_QUANTITY:
                raise ValidationError(
                    f"La cantidad total no puede superar {self.MAX_QUANTITY}"
                )
            existing.cantidad = new_quantity
        else:
            cart.items.append(
                CartItem(
                    product_id=product.id,
                    nombre=product.nombre,
                    precio=product.precio,
                    imagen=product.imagen,
                    cantidad=cantidad,
                )
            )

        return self._carts.save(cart)

    def update_item(self, *, user_id: str, product_id: str, cantidad: int) -> Cart:
        if cantidad < 1 or cantidad > self.MAX_QUANTITY:
            raise ValidationError(f"La cantidad debe estar entre 1 y {self.MAX_QUANTITY}")

        cart = self._carts.get_by_user(user_id)
        if cart is None:
            raise NotFoundError("Carrito no encontrado")

        item = self._carts.find_item(cart, product_id)
        if item is None:
            raise NotFoundError("Producto no encontrado en el carrito")

        item.cantidad = cantidad
        return self._carts.save(cart)

    def remove_item(self, *, user_id: str, product_id: str) -> Cart:
        cart = self._carts.get_by_user(user_id)
        if cart is None:
            raise NotFoundError("Carrito no encontrado")
        return self._carts.remove_item(cart, product_id)

    def clear(self, *, user_id: str) -> Cart:
        cart = self._carts.get_or_create(user_id)
        return self._carts.clear(cart)
