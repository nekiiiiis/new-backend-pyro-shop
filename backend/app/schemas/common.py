"""Esquemas base reutilizables.

El frontend Svelte espera identificadores de Mongo (`_id`, `createdAt`,
`updatedAt`). Para mantener el contrato sin tocar el cliente, los esquemas
de salida exponen esos alias.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MongoCompatModel(BaseModel):
    """Modelo base que genera campos compatibles con el contrato anterior."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampedModel(MongoCompatModel):
    """Añade los campos camelCase `createdAt` y `updatedAt`."""

    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class MessageResponse(BaseModel):
    message: str
