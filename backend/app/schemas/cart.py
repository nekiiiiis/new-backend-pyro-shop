"""Esquemas Pydantic del carrito."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import MongoCompatModel


class CartItemPublic(MongoCompatModel):
    product_id: str = Field(alias="productId")
    nombre: str
    precio: float
    imagen: Optional[str] = None
    cantidad: int = Field(ge=1)


class CartPublic(MongoCompatModel):
    id: str = Field(alias="_id")
    user_id: str = Field(alias="userId")
    items: List[CartItemPublic] = Field(default_factory=list)
    total: float = 0.0


class AddToCartRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_id: str = Field(alias="productId", min_length=1)
    cantidad: int = Field(default=1, ge=1, le=999)


class UpdateCartItemRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_id: str = Field(alias="productId", min_length=1)
    cantidad: int = Field(ge=1, le=999)


class CartResponse(BaseModel):
    message: str
    cart: CartPublic
