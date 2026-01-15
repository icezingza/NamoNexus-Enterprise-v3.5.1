import json
import os
from typing import Any, Dict, List, Optional

import requests


class ConversationalAgent:
    """Client wrapper for the /triage API with response metadata."""

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        timeout: float = 10.0,
        token: Optional[str] = None,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.chat_history: List[Dict[str, Any]] = []
        self._session = requests.Session()
        resolved_token = token or os.getenv("NAMO_NEXUS_TOKEN", "namo-nexus-enterprise-2026")
        self._headers = {"Authorization": f"Bearer {resolved_token}"}

    def chat(self, user_id: str, message: str) -> Dict[str, Any]:
        """Send a message and return response plus emotion metadata."""
        payload = {"user_id": user_id, "message": message}
        try:
            response = self._session.post(
                f"{self.api_url}/triage",
                json=payload,
                timeout=self.timeout,
                headers=self._headers,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            return {"error": f"api_request_failed: {exc}"}
        except json.JSONDecodeError:
            return {"error": "api_response_not_json"}

        risk_level = data.get("risk_level")
        risk_score = self._risk_level_score(risk_level)
        emotion_data = {
            "emotional_tone": data.get("emotional_tone"),
            "risk_level": risk_level,
            "risk_score": risk_score,
            "dharma_score": data.get("dharma_score"),
            "multimodal_confidence": data.get("multimodal_confidence"),
            "human_handoff_required": data.get("human_handoff_required"),
            "session_id": data.get("session_id"),
        }

        entry = {
            "user_id": user_id,
            "message": message,
            "response": data.get("response"),
            "emotion_data": emotion_data,
            "recommendations": [],
        }
        self.chat_history.append(entry)

        return {
            "response": entry["response"],
            "emotion": emotion_data,
            "recommendations": entry["recommendations"],
        }

    def analyze_emotion_changes(self, user_id: str) -> Dict[str, Any]:
        """Compare the first and latest emotion snapshots for a user."""
        user_history = [h for h in self.chat_history if h["user_id"] == user_id]
        if len(user_history) < 2:
            return {"result": "insufficient_data"}

        first = user_history[0]["emotion_data"]
        last = user_history[-1]["emotion_data"]

        first_risk = self._safe_float(first.get("risk_score"))
        last_risk = self._safe_float(last.get("risk_score"))
        if first_risk is None or last_risk is None:
            return {"result": "insufficient_data"}

        if last_risk < first_risk:
            trend = "improving"
        elif last_risk > first_risk:
            trend = "worsening"
        else:
            trend = "stable"

        return {
            "initial_tone": first.get("emotional_tone"),
            "current_tone": last.get("emotional_tone"),
            "initial_risk_score": first_risk,
            "current_risk_score": last_risk,
            "trend": trend,
            "message_count": len(user_history),
        }

    def get_recommendations(self, user_id: str) -> List[str]:
        """Collect all recommendations returned for a user."""
        user_history = [h for h in self.chat_history if h["user_id"] == user_id]
        recommendations: List[str] = []
        for entry in user_history:
            recommendations.extend(entry.get("recommendations", []))
        return recommendations

    @staticmethod
    def _safe_float(value: Optional[Any]) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _risk_level_score(risk_level: Optional[str]) -> Optional[float]:
        if not risk_level:
            return None
        mapping = {"low": 0.2, "moderate": 0.6, "severe": 1.0}
        return mapping.get(risk_level)


if __name__ == "__main__":
    agent = ConversationalAgent()
    result = agent.chat("user_001", "I feel anxious about tomorrow's exam.")
    print(json.dumps(result, indent=2))

    result = agent.chat("user_001", "I prepared well, so I might be okay.")
    print(json.dumps(result, indent=2))

    analysis = agent.analyze_emotion_changes("user_001")
    print(json.dumps(analysis, indent=2))
