"""Servicio para el CRUD de productos."""
from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Product, ProductCategory
from app.repositories import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Casos de uso sobre productos."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._products = ProductRepository(db)

    def list_products(self) -> List[Product]:
        return self._products.list_all()

    def get_product(self, product_id: str) -> Product:
        product = self._products.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Producto no encontrado")
        return product

    def create_product(self, payload: ProductCreate) -> Product:
        product = Product(
            nombre=payload.nombre,
            precio=payload.precio,
            descripcion=payload.descripcion,
            imagen=payload.imagen,
            categoria=ProductCategory(payload.categoria),
        )
        return self._products.create(product)

    def update_product(self, product_id: str, payload: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        data = payload.model_dump(exclude_unset=True)
        if "categoria" in data and data["categoria"] is not None:
            data["categoria"] = ProductCategory(data["categoria"])
        return self._products.update(product, data)

    def delete_product(self, product_id: str) -> None:
        product = self.get_product(product_id)
        self._products.delete(product)
