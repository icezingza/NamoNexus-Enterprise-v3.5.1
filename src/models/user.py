"""User models and schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.database.db import Base


class UserDB(Base):
    """User table."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    interaction_count = Column(Integer, default=0)

    interactions = relationship(
        "InteractionDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    memories = relationship(
        "MemoryDB",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserBase(BaseModel):
    """Base schema for user payloads."""

    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """Schema for creating users."""

    id: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    interaction_count: int
    is_active: bool


class UserUpdate(BaseModel):
    """Schema for updating users."""

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
