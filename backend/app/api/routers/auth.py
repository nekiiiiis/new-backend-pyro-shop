"""Router de autenticación: registro, login, perfil y cambio de contraseña."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginCredentials,
    RegisterCredentials,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserPublic, UserSummary
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterCredentials,
    service: AuthService = Depends(_service),
) -> AuthResponse:
    user, token = service.register(payload.username, payload.password)
    return AuthResponse(
        message="Usuario registrado exitosamente",
        token=token,
        user=UserSummary.model_validate({"id": user.id, "username": user.username, "role": user.role.value}),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginCredentials, service: AuthService = Depends(_service)) -> AuthResponse:
    user, token = service.login(payload.username, payload.password)
    return AuthResponse(
        message="Login exitoso",
        token=token,
        user=UserSummary.model_validate({"id": user.id, "username": user.username, "role": user.role.value}),
    )


@router.get("/me", response_model=UserPublic)
def me(
    current: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(_service),
) -> UserPublic:
    user = service.get_current_profile(current.id)
    return UserPublic.model_validate(
        {
            "_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "createdAt": user.created_at,
            "updatedAt": user.updated_at,
        }
    )


@router.put("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(_service),
) -> MessageResponse:
    service.change_password(current.id, payload.current_password, payload.new_password)
    return MessageResponse(message="Contraseña actualizada exitosamente")
