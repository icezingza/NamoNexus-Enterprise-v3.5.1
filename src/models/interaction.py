"""Interaction models and schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from src.database.db import Base


class InteractionDB(Base):
    """Conversation interaction table."""

    __tablename__ = "interactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user_message = Column(String, nullable=False)
    ai_response = Column(String, nullable=False)
    tone = Column(String)
    risk_level = Column(String)
    risk_score = Column(Float)
    coherence = Column(Float)
    moral_index = Column(Float)
    ethical_score = Column(Float)
    decision_consistency = Column(Float)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("UserDB", back_populates="interactions")


class InteractionCreate(BaseModel):
    """Schema for creating an interaction."""

    user_id: str
    user_message: str = Field(..., min_length=1, max_length=5000)
    ai_response: Optional[str] = None


class InteractionResponse(BaseModel):
    """Schema for interaction responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    user_message: str
    ai_response: str
    tone: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    coherence: Optional[float] = None
    moral_index: Optional[float] = None
    ethical_score: Optional[float] = None
    decision_consistency: Optional[float] = None
    recommendations: List[str]
    created_at: datetime
