"""Memory models and schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.db import Base


class MemoryDB(Base):
    """Persistent memory table."""

    __tablename__ = "memories"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    event = Column(String, nullable=False)
    emotion = Column(String, nullable=False)
    emotion_intensity = Column(Float)
    alignment_insight = Column(String)
    importance = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("UserDB", back_populates="memories")


class MemoryCreate(BaseModel):
    """Schema for creating memory records."""

    user_id: str
    event: str = Field(..., min_length=1, max_length=5000)
    emotion: str
    emotion_intensity: Optional[float] = None
    alignment_insight: Optional[str] = None
    importance: Optional[float] = None


class MemoryResponse(BaseModel):
    """Schema for memory responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    event: str
    emotion: str
    emotion_intensity: Optional[float] = None
    alignment_insight: Optional[str] = None
    importance: Optional[float] = None
    created_at: datetime
