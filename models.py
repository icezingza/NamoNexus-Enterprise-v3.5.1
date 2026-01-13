from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


class TriageRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    voice_features: Optional[Dict] = None
    facial_features: Optional[Dict] = None


class TriageResponse(BaseModel):
    response: str
    risk_level: Literal["low", "moderate", "severe"]
    dharma_score: float
    emotional_tone: str
    multimodal_confidence: float
    latency_ms: float
    session_id: str
    human_handoff_required: bool
    empathy_prompts: Optional[List[str]] = None


@dataclass
class MultiModalAnalysis:
    text_risk: float
    voice_stress: float
    facial_distress: float
    combined_risk: float
    confidence: float
