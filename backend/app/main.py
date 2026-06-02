"""Factoría de la aplicación FastAPI.

Mantiene la lógica de arranque mínima (config, CORS, exception handlers,
inicialización de BD y registro de routers). Toda la lógica de negocio
vive en `app.services` y el acceso a datos en `app.repositories`.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routers import auth, cart, orders, products, users
from app.core.config import get_settings
from app.core.database import SessionLocal, init_db
from app.core.exceptions import register_exception_handlers
from app.seeds import seed_initial_data

logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):  # noqa: D401
    """Ejecuta inicialización al arrancar y limpia al cerrar."""
    settings = get_settings()
    _configure_logging(settings.log_level)
    logger.info("Iniciando PyroShop API v%s (%s)", __version__, settings.app_env)

    init_db()
    if settings.seed_on_startup:
        with SessionLocal() as session:
            seed_initial_data(session)

    yield
    logger.info("Apagando PyroShop API")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="PyroShop API",
        version=__version__,
        description=(
            "Backend Python (FastAPI) para la plataforma PyroShop. "
            "Implementa autenticación JWT, validación con Pydantic, "
            "persistencia con SQLAlchemy y arquitectura en capas."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(users.router)
    app.include_router(cart.router)
    app.include_router(orders.router)

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok", "version": __version__}

    return app


app = create_app()
