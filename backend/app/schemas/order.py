"""Esquemas Pydantic de pedidos."""
from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field

from .common import MongoCompatModel, TimestampedModel

OrderStatusLiteral = Literal["pending", "completed"]


class OrderItemPublic(MongoCompatModel):
    product_id: str = Field(alias="productId")
    nombre: str
    precio: float
    cantidad: int
    subtotal: float


class OrderPublic(TimestampedModel):
    id: str = Field(alias="_id")
    user_id: str = Field(alias="userId")
    username: str
    items: List[OrderItemPublic]
    total: float
    status: OrderStatusLiteral


class OrderStatusUpdate(BaseModel):
    status: OrderStatusLiteral


class OrderResponse(BaseModel):
    message: str
    order: OrderPublic
