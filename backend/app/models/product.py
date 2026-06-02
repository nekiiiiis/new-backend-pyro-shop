"""Modelo ORM de productos."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProductCategory(str, enum.Enum):
    FUEGOS_ARTIFICIALES = "fuegos-artificiales"
    PETARDOS = "petardos"
    BENGALAS = "bengalas"
    COHETES = "cohetes"
    OTROS = "otros"


def _new_id() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    imagen: Mapped[str | None] = mapped_column(String(500), nullable=True)
    categoria: Mapped[ProductCategory] = mapped_column(
        Enum(ProductCategory, native_enum=False, length=32),
        default=ProductCategory.OTROS,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
