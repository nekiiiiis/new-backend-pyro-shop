"""Esquemas Pydantic relacionados con usuarios."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .common import MongoCompatModel, TimestampedModel

RoleLiteral = Literal["user", "admin"]


class UserPublic(TimestampedModel):
    """Representación pública (sin contraseña). Compatible con la antigua API."""

    id: str = Field(alias="_id")
    username: str
    role: RoleLiteral


class UserSummary(MongoCompatModel):
    """Versión reducida que devuelve `id` en lugar de `_id` (auth endpoints)."""

    id: str
    username: str
    role: RoleLiteral


class UserRoleUpdate(BaseModel):
    role: RoleLiteral


class UserRoleUpdateResponse(BaseModel):
    message: str
    user: UserPublic
