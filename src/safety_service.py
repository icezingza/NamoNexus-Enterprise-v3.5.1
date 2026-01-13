from typing import Dict, List

from src.config import config


class SafetyService:
    def __init__(self, critical_keywords: List[str] | None = None) -> None:
        keywords = critical_keywords if critical_keywords is not None else config.CRITICAL_KEYWORDS
        self.critical_keywords = [kw.lower() for kw in keywords]
        self.escalation_log: List[Dict[str, object]] = []

    def detect_critical_anomaly(self, text: str, user_id: str, intensity: float) -> Dict[str, object]:
        text_lower = text.lower()
        matched = [kw for kw in self.critical_keywords if kw in text_lower]
        signal_score = min(1.0, len(matched) * 0.25)
        intensity_score = min(1.0, intensity / 10.0)
        risk_score = round(min(1.0, (signal_score * 0.55) + (intensity_score * 0.45)), 2)
        if matched:
            # Treat explicit critical keywords as high risk regardless of intensity.
            risk_score = max(risk_score, 0.9)
        is_critical = risk_score >= 0.75
        return {
            "is_critical": is_critical,
            "risk_score": risk_score,
            "risk_level": "high" if is_critical else "low",
            "signals": matched,
            "user_id": user_id,
        }

    def emergency_redirection_gateway(self, user_id: str, message: str) -> Dict[str, object]:
        payload_preview = {
            "user_id": user_id,
            "summary": message[:160],
            "channel": "1323",
        }
        return {
            "ready": False,
            "endpoint": "https://hotline-1323.example/ingest",
            "payload_preview": payload_preview,
        }

    def handle_escalation(self, user_id: str, message: str, emotion: str) -> Dict[str, object]:
        gateway = self.emergency_redirection_gateway(user_id, message)
        response = {
            "user_id": user_id,
            "status": "ESCALATION_QUEUED",
            "risk_level": "high",
            "risk_score": 1.0,
            "message": "Immediate support recommended. Escalation has been queued.",
            "resources": [
                {"type": "hotline", "name": "Mental Health Support", "number": "1323"},
                {"type": "emergency", "name": "Emergency Services", "number": "1669"},
            ],
            "gateway": gateway,
            "emotion": emotion,
        }
        self.escalation_log.append(response)
        return response

    def validate_response_safety(self, response_text: str) -> Dict[str, object]:
        unsafe_patterns = [
            "you should hurt yourself",
            "take your life",
            "you are worthless",
            "nobody cares",
        ]
        is_safe = not any(pattern in response_text.lower() for pattern in unsafe_patterns)
        return {
            "is_safe": is_safe,
            "validation_passed": is_safe,
            "message": "Response is safe" if is_safe else "Response flagged for review",
        }


safety_service = SafetyService()
