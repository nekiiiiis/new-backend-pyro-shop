"""Carga inicial de datos para entornos de desarrollo.

Solo se ejecuta si la BD está vacía. Crea dos usuarios (admin/user) y un
puñado de productos representativos para que el frontend muestre algo
nada más arrancar.
"""
from __future__ import annotations

import logging
from typing import Iterable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import Product, ProductCategory, User, UserRole

logger = logging.getLogger(__name__)


_DEMO_PRODUCTS: Iterable[dict] = (
    {
        "nombre": "Cohete Supernova",
        "precio": 24.95,
        "descripcion": "Cohete pirotécnico con cola dorada y estallido multicolor.",
        "categoria": ProductCategory.COHETES,
        "imagen": "https://images.unsplash.com/photo-1530173568bd8?w=600",
    },
    {
        "nombre": "Bengala Estrella",
        "precio": 4.50,
        "descripcion": "Pack de 10 bengalas de larga duración (45s).",
        "categoria": ProductCategory.BENGALAS,
        "imagen": "https://images.unsplash.com/photo-1530173568bd8?w=600",
    },
    {
        "nombre": "Petardo Truenazo",
        "precio": 1.20,
        "descripcion": "Petardo de pólvora controlada, sonido grave.",
        "categoria": ProductCategory.PETARDOS,
        "imagen": "https://images.unsplash.com/photo-1530173568bd8?w=600",
    },
    {
        "nombre": "Torta Festival",
        "precio": 79.00,
        "descripcion": "Batería de 36 disparos en abanico con efectos crisantemo.",
        "categoria": ProductCategory.FUEGOS_ARTIFICIALES,
        "imagen": "https://images.unsplash.com/photo-1530173568bd8?w=600",
    },
)


def _create_user_if_missing(db: Session, *, username: str, password: str, role: UserRole) -> None:
    existing = db.query(User).filter(User.username == username).first()
    if existing is not None:
        return
    db.add(User(username=username, password_hash=hash_password(password), role=role))
    logger.info("Usuario semillado: %s (%s)", username, role.value)


def _create_products_if_empty(db: Session) -> None:
    if db.query(Product).count() > 0:
        return
    for data in _DEMO_PRODUCTS:
        db.add(Product(**data))
    logger.info("Productos demo insertados: %d", sum(1 for _ in _DEMO_PRODUCTS))


def seed_initial_data(db: Session) -> None:
    """Crea usuarios y productos demo si la BD está vacía."""
    settings = get_settings()
    if not settings.seed_on_startup:
        return

    _create_user_if_missing(
        db,
        username=settings.seed_admin_username,
        password=settings.seed_admin_password,
        role=UserRole.ADMIN,
    )
    _create_user_if_missing(
        db,
        username=settings.seed_user_username,
        password=settings.seed_user_password,
        role=UserRole.USER,
    )
    _create_products_if_empty(db)

    db.commit()
