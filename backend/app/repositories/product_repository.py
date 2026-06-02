"""Repositorio de productos."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product


class ProductRepository:
    """Operaciones SQL para productos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._db.get(Product, product_id)

    def list_all(self) -> List[Product]:
        stmt = select(Product).order_by(Product.created_at.desc())
        return list(self._db.execute(stmt).scalars().all())

    def create(self, product: Product) -> Product:
        self._db.add(product)
        self._db.commit()
        self._db.refresh(product)
        return product

    def update(self, product: Product, fields: dict) -> Product:
        for key, value in fields.items():
            if value is not None:
                setattr(product, key, value)
        self._db.commit()
        self._db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self._db.delete(product)
        self._db.commit()

    def count(self) -> int:
        return self._db.query(Product).count()
