"""Repository helpers for database access."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.models.interaction import InteractionDB
from src.models.memory import MemoryDB
from src.models.user import UserDB


class UserRepository:
    """Repository for user records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, user_id: str, username: Optional[str] = None, email: Optional[str] = None) -> UserDB:
        db_user = UserDB(
            id=user_id,
            username=username or user_id,
            email=email,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.username == username).first()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserDB]:
        return self.db.query(UserDB).offset(skip).limit(limit).all()

    def get_or_create(self, user_id: str) -> UserDB:
        user = self.get_user_by_id(user_id)
        if user:
            return user
        return self.create_user(user_id=user_id)

    def increment_interaction_count(self, user_id: str) -> None:
        user = self.get_user_by_id(user_id)
        if not user:
            return
        user.interaction_count += 1
        self.db.commit()


class InteractionRepository:
    """Repository for interactions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_interaction(self, interaction_data: dict) -> InteractionDB:
        db_interaction = InteractionDB(
            id=str(uuid.uuid4()),
            **interaction_data,
        )
        self.db.add(db_interaction)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def get_user_interactions(self, user_id: str, limit: int = 50) -> List[InteractionDB]:
        return (
            self.db.query(InteractionDB)
            .filter(InteractionDB.user_id == user_id)
            .order_by(desc(InteractionDB.created_at))
            .limit(limit)
            .all()
        )

    def get_interaction_by_id(self, interaction_id: str) -> Optional[InteractionDB]:
        return self.db.query(InteractionDB).filter(InteractionDB.id == interaction_id).first()


class MemoryRepository:
    """Repository for memory records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_memory(self, memory_data: dict) -> MemoryDB:
        db_memory = MemoryDB(
            id=str(uuid.uuid4()),
            **memory_data,
        )
        self.db.add(db_memory)
        self.db.commit()
        self.db.refresh(db_memory)
        return db_memory

    def get_user_memories(self, user_id: str, days_back: int = 30) -> List[MemoryDB]:
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        return (
            self.db.query(MemoryDB)
            .filter(MemoryDB.user_id == user_id, MemoryDB.created_at >= cutoff)
            .order_by(desc(MemoryDB.created_at))
            .all()
        )

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryDB]:
        return self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
