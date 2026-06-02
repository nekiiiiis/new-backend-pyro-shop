"""Esquemas Pydantic de productos."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampedModel

CategoryLiteral = Literal[
    "fuegos-artificiales",
    "petardos",
    "bengalas",
    "cohetes",
    "otros",
]


class ProductBase(BaseModel):
    """Campos comunes de creación/edición."""

    model_config = ConfigDict(extra="ignore")

    nombre: str = Field(min_length=1, max_length=120)
    precio: float = Field(ge=0)
    descripcion: str = Field(min_length=1, max_length=2000)
    imagen: Optional[str] = Field(default=None, max_length=500)
    categoria: CategoryLiteral = Field(default="otros")


class ProductCreate(ProductBase):
    """Payload de creación. Todos los campos obligatorios excepto `imagen`."""


class ProductUpdate(BaseModel):
    """Payload de actualización: todos los campos opcionales."""

    model_config = ConfigDict(extra="ignore")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=120)
    precio: Optional[float] = Field(default=None, ge=0)
    descripcion: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    imagen: Optional[str] = Field(default=None, max_length=500)
    categoria: Optional[CategoryLiteral] = None


class ProductPublic(TimestampedModel):
    id: str = Field(alias="_id")
    nombre: str
    precio: float
    descripcion: str
    imagen: Optional[str] = None
    categoria: CategoryLiteral
