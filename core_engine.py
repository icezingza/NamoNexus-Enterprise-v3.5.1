from __future__ import annotations

import asyncio
from typing import Dict, Optional

from models import MultiModalAnalysis


class DhammicDataLake:
    """Central dharma ruleset for ethical calibration and safety checks."""

    CORE_PRINCIPLES = {
        "right_speech": {
            "keywords": ["สัตย์", "จริง", "ถูกต้อง", "ประโยชน์", "สันติ"],
            "weight": 0.35,
        },
        "compassion": {
            "keywords": ["เมตตา", "กรุณา", "ช่วยเหลือ", "อนุเคราะห์", "เห็นใจ"],
            "weight": 0.35,
        },
        "mindfulness": {
            "keywords": ["สติ", "ระลึก", "รู้ตัว", "ตระหนัก", "รู้เท่าทัน"],
            "weight": 0.30,
        },
    }

    SAFETY_CONSTRAINTS = {
        "high_risk_patterns": ["ฆ่าตัวตาย", "ทำร้ายตัวเอง", "อยากตาย", "หมดหวัง"],
        "immediate_escalation": ["กำลังจะ", "วันนี้จะ", "เตรียม"],
    }

    @classmethod
    def calculate_dharma_alignment(cls, text: str) -> Dict:
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
    def check_safety(cls, text: str) -> Dict:
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
        self.dhammic_lake = DhammicDataLake()

    async def analyze_text(self, text: str) -> float:
        await asyncio.sleep(0.02)
        depression_keywords = ["เศร้า", "ทุกข์", "หมดหวัง", "เหนื่อย", "ไม่มีแรง"]
        severity_keywords = ["มาก", "ทุกวัน", "ตลอดเวลา", "ไม่หยุด"]

        text_lower = text.lower()
        base_score = sum(0.15 for keyword in depression_keywords if keyword in text_lower)
        severity_multiplier = 1.5 if any(
            keyword in text_lower for keyword in severity_keywords
        ) else 1.0

        return min(base_score * severity_multiplier, 1.0)

    async def analyze_voice(self, voice_features: Optional[Dict]) -> float:
        await asyncio.sleep(0.02)
        if not voice_features:
            return 0.5

        pitch_variance = voice_features.get("pitch_variance", 0.5)
        speech_rate = voice_features.get("speech_rate", 0.5)
        energy = voice_features.get("energy", 0.5)

        return (1 - energy) * 0.4 + (1 - speech_rate) * 0.3 + (1 - pitch_variance) * 0.3

    async def analyze_facial(self, facial_features: Optional[Dict]) -> float:
        await asyncio.sleep(0.02)
        if not facial_features:
            return 0.5

        inner_brow_raise = facial_features.get("au1", 0)
        outer_brow_raise = facial_features.get("au2", 0)
        lip_corner_depressor = facial_features.get("au15", 0)

        return (
            inner_brow_raise * 0.4
            + outer_brow_raise * 0.3
            + lip_corner_depressor * 0.3
        )

    async def multimodal_fusion(
        self,
        text: str,
        voice_features: Optional[Dict],
        facial_features: Optional[Dict],
    ) -> MultiModalAnalysis:
        text_risk, voice_stress, facial_distress = await asyncio.gather(
            self.analyze_text(text),
            self.analyze_voice(voice_features),
            self.analyze_facial(facial_features),
        )

        weights = {
            "text": 0.5,
            "voice": 0.3 if voice_features else 0.0,
            "facial": 0.2 if facial_features else 0.0,
        }
        total_weight = sum(weights.values()) or 1.0
        normalized = {key: value / total_weight for key, value in weights.items()}

        combined = (
            text_risk * normalized["text"]
            + voice_stress * normalized["voice"]
            + facial_distress * normalized["facial"]
        )

        modalities_count = 1 + int(bool(voice_features)) + int(bool(facial_features))
        confidence = min(0.5 + (modalities_count * 0.25), 1.0)

        return MultiModalAnalysis(
            text_risk=text_risk,
            voice_stress=voice_stress,
            facial_distress=facial_distress,
            combined_risk=combined,
            confidence=confidence,
        )


class EthicalCalibrationKernel:
    """Dhammic moat calibration for tone and safety."""

    def __init__(self) -> None:
        self.lake = DhammicDataLake()
        self.ethics_score_threshold = 0.6

    async def calibrate(self, text: str, multimodal: MultiModalAnalysis) -> Dict:
        dharma = self.lake.calculate_dharma_alignment(text)
        safety = self.lake.check_safety(text)

        if multimodal.combined_risk > 0.7:
            tone = "compassionate"
        elif multimodal.combined_risk > 0.4:
            tone = "supportive"
        else:
            tone = "positive"

        return {
            "dharma_score": dharma["dharma_score"],
            "principles": dharma["principles"],
            "risk_level": safety["risk_level"],
            "requires_human": safety["requires_human"],
            "emotional_tone": tone,
            "intervention": safety["intervention_type"],
            "ethics_passed": True,
        }


class HarmonicGovernor:
    """Orchestrates triage, ethics calibration, and auditing."""

    def __init__(self) -> None:
        self.agents = {
            "triage": MultiModalTriageEngine(),
            "ethics": EthicalCalibrationKernel(),
            "conversation": None,
            "auditor": self._create_auditor(),
        }

    def _create_auditor(self):
        class Auditor:
            def audit(self, ethics_result: Dict) -> Dict:
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
    ) -> Dict:
        multimodal = await self.agents["triage"].multimodal_fusion(
            message, voice_features, facial_features
        )
        ethics = await self.agents["ethics"].calibrate(message, multimodal)
        audit = self.agents["auditor"].audit(ethics)

        if audit["needs_healing"]:
            ethics["dharma_score"] = 0.5

        return {
            "multimodal": multimodal,
            "ethics": ethics,
            "audit": audit,
        }
