from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class VoiceFeatures(BaseModel):
    pitch_variance: float = Field(..., ge=0.0, le=1.0)
    speech_rate: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)


class FacialFeatures(BaseModel):
    au1: float = Field(..., ge=0.0, le=1.0)
    au2: float = Field(..., ge=0.0, le=1.0)
    au15: float = Field(..., ge=0.0, le=1.0)


class _MessageRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5_000)

    @field_validator("user_id")
    @classmethod
    def no_control_chars_user_id(cls, value: str) -> str:
        if any(ord(char) < 32 and char not in "\t\n\r" for char in value):
            raise ValueError("User ID contains control characters")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("User ID cannot be empty")
        return cleaned

    @field_validator("message")
    @classmethod
    def no_control_chars(cls, value: str) -> str:
        if any(ord(char) < 32 and char not in "\t\n\r" for char in value):
            raise ValueError("Message contains control characters")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty")
        return cleaned


class TriageRequest(_MessageRequest):
    session_id: Optional[str] = Field(None, max_length=255)
    voice_features: Optional[VoiceFeatures] = None
    facial_features: Optional[FacialFeatures] = None


class InteractRequest(_MessageRequest):
    pass


class ReflectRequest(_MessageRequest):
    session_id: Optional[str] = Field(None, max_length=255)
