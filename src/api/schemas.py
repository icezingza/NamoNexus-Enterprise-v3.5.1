"""Pydantic schemas for API payloads."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class UserMessage(BaseModel):
    """Incoming message payload."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: str = "anonymous"
    message: Optional[str] = None
    text: Optional[str] = None
    previous_emotion: Optional[str] = None

    @model_validator(mode="after")
    def ensure_message(self) -> "UserMessage":
        content = self.message.strip() if self.message is not None else None
        if not content:
            content = self.text.strip() if self.text is not None else None
        if not content:
            raise ValueError("message is required")
        self.message = content
        return self


class InteractionResponse(BaseModel):
    """Standard response for /interact and /reflect."""

    is_refusal: Optional[bool] = False
    user_id: str
    response: str
    reflection_text: str
    tone: str
    risk_level: str
    risk_score: float
    coherence: float
    moral_index: float
    ethical_score: float
    decision_consistency: float
    recommendations: List[str]
