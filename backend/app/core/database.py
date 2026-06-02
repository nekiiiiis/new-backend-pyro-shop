"""Infraestructura SQLAlchemy: engine, sesión y base declarativa.

La función `get_db` se usa como dependencia de FastAPI para inyectar
una sesión por petición y garantizar su cierre incluso ante excepciones.
"""
from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


def _build_engine() -> Engine:
    settings = get_settings()
    connect_args: dict = {}

    if settings.database_url.startswith("sqlite"):
        # SQLite + threading: required when multiple workers comparten conexión
        connect_args["check_same_thread"] = False
        # Asegurar que el directorio del fichero existe
        path = settings.database_url.replace("sqlite:///", "", 1)
        if path and path != ":memory:":
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)

    return create_engine(
        settings.database_url,
        echo=False,
        future=True,
        connect_args=connect_args,
    )


engine: Engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa común para todos los modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI que abre y cierra una sesión por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea las tablas si no existen (modo desarrollo).

    Para entornos productivos sería preferible usar Alembic, pero para los
    objetivos de esta práctica `create_all` es suficiente y reproducible.
    """
    # Importación tardía para registrar los modelos en `Base.metadata`.
    from app import models  # noqa: F401  (registro de metadata)

    Base.metadata.create_all(bind=engine)
