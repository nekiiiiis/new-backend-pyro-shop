"""Repositorio de usuarios."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserRole


class UserRepository:
    """Encapsula las operaciones SQL relacionadas con usuarios."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._db.get(User, user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[User]:
        stmt = select(User).order_by(User.created_at.desc())
        return list(self._db.execute(stmt).scalars().all())

    def create(self, *, username: str, password_hash: str, role: UserRole = UserRole.USER) -> User:
        user = User(username=username, password_hash=password_hash, role=role)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update_role(self, user: User, role: UserRole) -> User:
        user.role = role
        self._db.commit()
        self._db.refresh(user)
        return user

    def update_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        self._db.commit()
        self._db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self._db.delete(user)
        self._db.commit()
