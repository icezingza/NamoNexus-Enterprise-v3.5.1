from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


class VoiceFeaturesInput(BaseModel):
    """Validated voice features input.
    
    These features represent acoustic characteristics that may indicate
    emotional distress. All values should be normalized to 0-1 range.
    """
    pitch_variance: float = Field(
        ge=0, le=1, default=0.5,
        description="Pitch variance (0=flat affect, 1=highly variable)"
    )
    speech_rate: float = Field(
        ge=0, le=1, default=0.5,
        description="Speech rate (0=very slow, 1=very fast)"
    )
    energy: float = Field(
        ge=0, le=1, default=0.5,
        description="Voice energy/volume (0=quiet/weak, 1=loud/strong)"
    )


class FacialFeaturesInput(BaseModel):
    """Validated facial features input (Action Units).
    
    Based on Facial Action Coding System (FACS).
    Reserved for future implementation.
    """
    au1: float = Field(
        ge=0, le=1, default=0,
        description="AU1: Inner Brow Raise (sadness indicator)"
    )
    au2: float = Field(
        ge=0, le=1, default=0,
        description="AU2: Outer Brow Raise"
    )
    au15: float = Field(
        ge=0, le=1, default=0,
        description="AU15: Lip Corner Depressor (sadness indicator)"
    )


class TriageRequest(BaseModel):
    """Request for text-based triage with optional multimodal features."""
    message: str
    user_id: str
    session_id: Optional[str] = None
    voice_features: Optional[Union[VoiceFeaturesInput, Dict]] = None
    facial_features: Optional[Union[FacialFeaturesInput, Dict]] = None
    
    @model_validator(mode='before')
    @classmethod
    def convert_features(cls, values):
        """Convert dict features to validated models."""
        if isinstance(values.get('voice_features'), dict):
            values['voice_features'] = VoiceFeaturesInput(**values['voice_features'])
        if isinstance(values.get('facial_features'), dict):
            values['facial_features'] = FacialFeaturesInput(**values['facial_features'])
        return values


class AudioTriageRequest(BaseModel):
    """Request metadata for audio-based triage.
    
    Used with multipart/form-data when uploading audio files.
    """
    user_id: str
    session_id: Optional[str] = None
    message: Optional[str] = Field(
        default=None,
        description="Optional text message. If not provided, will be transcribed from audio."
    )


class TriageResponse(BaseModel):
    """Response from triage endpoint."""
    response: str
    risk_level: Literal["low", "moderate", "severe"]
    dharma_score: float
    emotional_tone: str
    multimodal_confidence: float
    latency_ms: float
    session_id: str
    human_handoff_required: bool
    empathy_prompts: Optional[List[str]] = None
    transcription: Optional[str] = None  # Added for audio triage


@dataclass
class MultiModalAnalysis:
    """Internal multimodal analysis result."""
    text_risk: float
    voice_stress: float
    facial_distress: float
    combined_risk: float
    confidence: float
    text_confidence: float = 0.0
    voice_confidence: float = 0.0
    facial_confidence: float = 0.0
    risk_factors: Optional[List[str]] = None
