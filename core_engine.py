from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from models import MultiModalAnalysis
from src.i18n import load_locale

PHI = (1 + 5**0.5) / 2
INV_PHI = PHI - 1
REMAINDER = 1 - INV_PHI
GOLDEN_RATIO = PHI
_LOCALE = load_locale("th")
_CORE_CONFIG = _LOCALE["core_engine"]


def calculate_harmonic_risk(primary_risk: float, secondary_risk: float) -> float:
    """Blend two risk signals using golden ratio weighting."""
    blended = (primary_risk * GOLDEN_RATIO + secondary_risk) / (GOLDEN_RATIO + 1)
    return max(0.0, min(1.0, blended))


class DhammicDataLake:
    """Central dharma ruleset and lightweight insight store."""

    CORE_PRINCIPLES = _CORE_CONFIG["core_principles"]
    SAFETY_CONSTRAINTS = _CORE_CONFIG["safety_constraints"]

    def __init__(self) -> None:
        self.logger = logging.getLogger("namo_nexus.datalake")
        self.cache: Dict[str, Dict[str, Any]] = {}

    async def store_insight(self, key: str, data: Any) -> bool:
        try:
            self.cache[key] = {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            return True
        except Exception as exc:
            self.logger.error("Failed to store insight: %s", exc, exc_info=True)
            return False

    @classmethod
    def calculate_dharma_alignment(cls, text: str) -> Dict[str, Any]:
        score = 0.0
        matched = []
        text_lower = text.lower()

        for principle, config in cls.CORE_PRINCIPLES.items():
            if any(keyword in text_lower for keyword in config["keywords"]):
                score += config["weight"]
                matched.append(principle)

        return {
            "dharma_score": min(score, 1.0),
            "principles": matched,
            "aligned": score > 0.3,
        }

    @classmethod
    def check_safety(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        high_risk = any(
            pattern in text_lower for pattern in cls.SAFETY_CONSTRAINTS["high_risk_patterns"]
        )
        immediate = any(
            pattern in text_lower for pattern in cls.SAFETY_CONSTRAINTS["immediate_escalation"]
        )

        risk_level = "severe" if (high_risk and immediate) else "moderate" if high_risk else "low"
        return {
            "is_safe": True,
            "risk_level": risk_level,
            "requires_human": risk_level == "severe",
            "intervention_type": "compassionate_support",
        }


class MultiModalTriageEngine:
    """Multimodal triage combining text, voice, and facial cues."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("namo_nexus.triage")
        self.dhammic_lake = DhammicDataLake()
        self.text_patterns = _CORE_CONFIG["text_patterns"]

    def _validate_input(
        self,
        message: str,
        voice_features: Optional[Dict],
        facial_features: Optional[Dict],
    ) -> None:
        if not isinstance(message, str):
            raise TypeError(f"Message must be string, got {type(message)}")
        if not message.strip():
            raise ValueError("Message cannot be empty")
        if voice_features is not None and not isinstance(voice_features, dict):
            raise TypeError(f"Voice features must be dict, got {type(voice_features)}")
        if facial_features is not None and not isinstance(facial_features, dict):
            raise TypeError(f"Facial features must be dict, got {type(facial_features)}")

    async def _analyze_text_ml_ready(self, text: str) -> Dict[str, Any]:
        # ML-ready hook: swap keyword matching with transformer inference later.
        text_lower = text.lower()
        depression_keywords = _CORE_CONFIG["depression_keywords"]
        severity_keywords = _CORE_CONFIG["severity_keywords"]

        base_score = sum(0.15 for keyword in depression_keywords if keyword in text_lower)
        severity_multiplier = 1.5 if any(
            keyword in text_lower for keyword in severity_keywords
        ) else 1.0
        risk_score = min(0.1 + (base_score * severity_multiplier), 1.0)
        confidence = 0.5 + min(base_score, 0.4)
        matched_category = "low"

        for category, keywords in self.text_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                if category == "severe":
                    risk_score = max(risk_score, 0.9)
                    confidence = max(confidence, 0.95)
                elif category == "high":
                    risk_score = max(risk_score, 0.7)
                    confidence = max(confidence, 0.85)
                elif category == "moderate":
                    risk_score = max(risk_score, 0.5)
                    confidence = max(confidence, 0.75)
                matched_category = category
                break

        return {
            "risk_score": min(risk_score, 1.0),
            "confidence": min(confidence, 1.0),
            "category": matched_category,
            "method": "keyword_matching",
        }

    async def _analyze_voice_ml_ready(self, voice_features: Dict[str, float]) -> Dict[str, Any]:
        if not voice_features:
            return {
                "risk_score": 0.0,
                "confidence": 0.0,
                "risk_factors": [],
                "method": "no_data",
            }

        risk_score = 0.0
        confidence = 0.6
        risk_factors = []

        energy = voice_features.get("energy", 0.5)
        if energy < 0.2:
            risk_score += 0.5
            risk_factors.append("very_low_energy")
        elif energy < 0.4:
            risk_score += 0.3
            risk_factors.append("low_energy")

        pitch_variance = voice_features.get("pitch_variance", 0.0)
        if pitch_variance > 0.8:
            risk_score += 0.4
            risk_factors.append("high_pitch_variance")

        tremor = voice_features.get("tremor", 0.0)
        if tremor > 0.7:
            risk_score += 0.3
            risk_factors.append("voice_tremor")

        speech_rate = voice_features.get("speech_rate", 1.0)
        if speech_rate < 0.5 or speech_rate > 2.0:
            risk_score += 0.2
            risk_factors.append("abnormal_speech_rate")

        pause_duration = voice_features.get("pause_duration", 0.0)
        if pause_duration > 0.7:
            risk_score += 0.2
            risk_factors.append("long_pauses")

        return {
            "risk_score": min(risk_score, 1.0),
            "confidence": min(confidence, 1.0),
            "risk_factors": risk_factors,
            "method": "feature_heuristics",
        }

    async def _analyze_facial_ml_ready(self, facial_features: Dict[str, float]) -> Dict[str, Any]:
        if not facial_features:
            return {"risk_score": 0.0, "confidence": 0.0, "method": "no_data"}

        inner_brow_raise = facial_features.get("au1", 0.0)
        outer_brow_raise = facial_features.get("au2", 0.0)
        lip_corner_depressor = facial_features.get("au15", 0.0)

        risk_score = (
            inner_brow_raise * 0.4
            + outer_brow_raise * 0.3
            + lip_corner_depressor * 0.3
        )
        return {
            "risk_score": min(risk_score, 1.0),
            "confidence": 0.55,
            "method": "facial_heuristics",
        }

    async def analyze_text(self, text: str) -> float:
        analysis = await self._analyze_text_ml_ready(text)
        return analysis["risk_score"]

    async def analyze_voice(self, voice_features: Optional[Dict]) -> float:
        analysis = await self._analyze_voice_ml_ready(voice_features or {})
        return analysis["risk_score"]

    async def analyze_facial(self, facial_features: Optional[Dict]) -> float:
        analysis = await self._analyze_facial_ml_ready(facial_features or {})
        return analysis["risk_score"]

    async def multimodal_fusion(
        self,
        text: str,
        voice_features: Optional[Dict],
        facial_features: Optional[Dict],
    ) -> MultiModalAnalysis:
        self._validate_input(text, voice_features, facial_features)
        try:
            text_analysis, voice_analysis, facial_analysis = await asyncio.gather(
                self._analyze_text_ml_ready(text),
                self._analyze_voice_ml_ready(voice_features or {}),
                self._analyze_facial_ml_ready(facial_features or {}),
            )

            weights = {
                "text": REMAINDER,
                "voice": INV_PHI if voice_features else 0.0,
                "facial": 0.2 if facial_features else 0.0,
            }
            total_weight = sum(weights.values()) or 1.0
            normalized = {key: value / total_weight for key, value in weights.items()}

            combined = (
                text_analysis["risk_score"] * normalized["text"]
                + voice_analysis["risk_score"] * normalized["voice"]
                + facial_analysis["risk_score"] * normalized["facial"]
            )
            confidence = (
                text_analysis["confidence"] * normalized["text"]
                + voice_analysis["confidence"] * normalized["voice"]
                + facial_analysis["confidence"] * normalized["facial"]
            )
            combined = min(max(combined, 0.0), 1.0)
            confidence = min(max(confidence, 0.0), 1.0)

            result = MultiModalAnalysis(
                text_risk=text_analysis["risk_score"],
                voice_stress=voice_analysis["risk_score"],
                facial_distress=facial_analysis["risk_score"],
                combined_risk=combined,
                confidence=confidence,
                text_confidence=text_analysis["confidence"],
                voice_confidence=voice_analysis["confidence"],
                facial_confidence=facial_analysis["confidence"],
                risk_factors=voice_analysis.get("risk_factors", []),
            )

            await self.dhammic_lake.store_insight(
                key=f"triage_{datetime.utcnow().timestamp()}",
                data={
                    "text": text_analysis,
                    "voice": voice_analysis,
                    "facial": facial_analysis,
                    "combined": combined,
                    "confidence": confidence,
                },
            )

            self.logger.info(
                "Multimodal fusion complete score=%.3f confidence=%.2f",
                combined,
                confidence,
            )
            return result
        except Exception as exc:
            self.logger.error("Multimodal fusion failed: %s", exc, exc_info=True)
            raise


class EthicalCalibrationKernel:
    """Dhammic moat calibration for tone and safety."""

    def __init__(self) -> None:
        self.lake = DhammicDataLake()
        self.logger = logging.getLogger("namo_nexus.ethics")
        self.ethics_score_threshold = 0.6

    @staticmethod
    def _recommendation_for_score(score: float) -> str:
        if score > 0.7:
            return "immediate_intervention"
        if score > 0.5:
            return "urgent_support"
        if score > 0.3:
            return "scheduled_support"
        return "monitoring"

    async def calibrate(self, text: str, multimodal: MultiModalAnalysis) -> Dict[str, Any]:
        text_lower = text.lower()
        dharma = self.lake.calculate_dharma_alignment(text)
        safety = self.lake.check_safety(text)
        safety_keywords = (
            self.lake.SAFETY_CONSTRAINTS["high_risk_patterns"]
            + self.lake.SAFETY_CONSTRAINTS["immediate_escalation"]
        )
        keyword_flag = any(keyword in text_lower for keyword in safety_keywords)
        ethics_passed = not (keyword_flag and multimodal.combined_risk > 0.7)

        if multimodal.combined_risk > 0.7:
            tone = "compassionate"
        elif multimodal.combined_risk > 0.4:
            tone = "supportive"
        else:
            tone = "positive"

        recommendation = self._recommendation_for_score(multimodal.combined_risk)
        result = {
            "dharma_score": dharma["dharma_score"],
            "principles": dharma["principles"],
            "risk_level": safety["risk_level"],
            "requires_human": safety["requires_human"],
            "emotional_tone": tone,
            "intervention": safety["intervention_type"],
            "ethics_passed": ethics_passed,
            "recommendation": recommendation,
        }
        self.logger.info(
            "Ethics calibrated risk=%s recommendation=%s",
            result["risk_level"],
            recommendation,
        )
        return result


class HarmonicGovernor:
    """Orchestrates triage, ethics calibration, and auditing."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("namo_nexus.governor")
        self.agents = {
            "triage": MultiModalTriageEngine(),
            "ethics": EthicalCalibrationKernel(),
            "conversation": None,
            "auditor": self._create_auditor(),
        }

    def _create_auditor(self):
        class Auditor:
            def audit(self, ethics_result: Dict[str, Any]) -> Dict[str, Any]:
                score = ethics_result.get("dharma_score", 0)
                return {
                    "passed": score >= 0.3,
                    "needs_healing": score < 0.2,
                    "audit_score": score,
                }

        return Auditor()

    async def orchestrate(
        self,
        message: str,
        voice_features: Optional[Dict],
        facial_features: Optional[Dict],
    ) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        try:
            multimodal = await self.agents["triage"].multimodal_fusion(
                message, voice_features, facial_features
            )
            ethics = await self.agents["ethics"].calibrate(message, multimodal)
            audit = self.agents["auditor"].audit(ethics)

            if audit["needs_healing"]:
                ethics["dharma_score"] = 0.5

            await self.agents["triage"].dhammic_lake.store_insight(
                key=f"orchestrate_{datetime.utcnow().timestamp()}",
                data={
                    "ethics": ethics,
                    "audit": audit,
                    "multimodal": {
                        "combined_risk": multimodal.combined_risk,
                        "confidence": multimodal.confidence,
                        "risk_factors": multimodal.risk_factors or [],
                    },
                },
            )

            return {
                "multimodal": multimodal,
                "ethics": ethics,
                "audit": audit,
                "timestamp": timestamp,
                "phi_version": f"{PHI:.11f}",
            }
        except Exception as exc:
            self.logger.error("Orchestration failed: %s", exc, exc_info=True)
            raise
