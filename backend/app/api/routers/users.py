"""Router de usuarios (solo admin)."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_admin, get_db
from app.models import User
from app.schemas.common import MessageResponse
from app.schemas.user import UserPublic, UserRoleUpdate, UserRoleUpdateResponse
from app.services import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


def _service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def _to_public(user: User) -> UserPublic:
    return UserPublic.model_validate(
        {
            "_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "createdAt": user.created_at,
            "updatedAt": user.updated_at,
        }
    )


@router.get("", response_model=List[UserPublic])
def list_users(
    _: CurrentUser = Depends(get_current_admin),
    service: UserService = Depends(_service),
) -> List[UserPublic]:
    return [_to_public(u) for u in service.list_users()]


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: str,
    _: CurrentUser = Depends(get_current_admin),
    service: UserService = Depends(_service),
) -> UserPublic:
    user = service.get_user(user_id)
    return _to_public(user)


@router.put("/{user_id}/role", response_model=UserRoleUpdateResponse)
def update_role(
    user_id: str,
    payload: UserRoleUpdate,
    current: CurrentUser = Depends(get_current_admin),
    service: UserService = Depends(_service),
) -> UserRoleUpdateResponse:
    user = service.update_role(user_id=user_id, role=payload.role, requester_id=current.id)
    return UserRoleUpdateResponse(message="Rol actualizado correctamente", user=_to_public(user))


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: str,
    current: CurrentUser = Depends(get_current_admin),
    service: UserService = Depends(_service),
) -> MessageResponse:
    service.delete_user(user_id=user_id, requester_id=current.id)
    return MessageResponse(message="Usuario eliminado correctamente")
