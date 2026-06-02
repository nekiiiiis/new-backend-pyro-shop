"""Excepciones de dominio y manejadores globales de errores.

Las excepciones de la capa de servicios extienden `DomainError` para que
los routers nunca tengan que conocer detalles de HTTP. El manejador global
las traduce a respuestas JSON limpias y unificadas.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .config import get_settings

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Error de lógica de negocio. Trae mensaje + status HTTP sugerido."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class ValidationError(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT


class AuthenticationError(DomainError):
    status_code = status.HTTP_401_UNAUTHORIZED


class AuthorizationError(DomainError):
    status_code = status.HTTP_403_FORBIDDEN


def _error_payload(message: str, **extra: Any) -> Dict[str, Any]:
    """Estructura unificada de error compatible con el frontend.

    El cliente Svelte espera `error` o `message` como string; mantenemos
    `error` para coincidir con el contrato del backend anterior.
    """
    payload: Dict[str, Any] = {"error": message}
    if extra:
        payload.update(extra)
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales en la app FastAPI."""

    settings = get_settings()

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.message),
        )

    @app.exception_handler(HTTPException)
    async def _handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Error en la petición"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Construye un mensaje legible con el primer error y expone el detalle estructurado.
        errors = exc.errors()
        first = errors[0] if errors else None
        message = "Datos de entrada inválidos"
        if first:
            loc = ".".join(str(part) for part in first.get("loc", []) if part != "body")
            field = loc or "payload"
            message = f"{field}: {first.get('msg', 'valor inválido')}"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(message, details=errors),
        )

    @app.exception_handler(IntegrityError)
    async def _handle_integrity_error(_: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("Conflicto de integridad en BD: %s", exc.orig)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_payload("Conflicto: el recurso ya existe o viola una restricción."),
        )

    @app.exception_handler(SQLAlchemyError)
    async def _handle_db_error(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.exception("Error de base de datos", exc_info=exc)
        message = "Error de base de datos" if settings.is_production else str(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(message),
        )

    @app.exception_handler(Exception)
    async def _handle_unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error no controlado", exc_info=exc)
        message = "Error interno del servidor" if settings.is_production else str(exc) or "Error interno"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(message),
        )


__all__ = [
    "DomainError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "AuthenticationError",
    "AuthorizationError",
    "register_exception_handlers",
]
