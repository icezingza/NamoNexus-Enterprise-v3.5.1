"""Emotion analysis service with basic heuristics."""

from __future__ import annotations

from typing import Dict

from src.i18n import load_locale
from src.utils.exceptions import InvalidInputError, ServiceError
from src.utils.logger import logger


class EmotionService:
    """Analyze emotional tone from text."""

    def analyze_sentiment(self, text: str) -> Dict[str, object]:
        """Return emotion, intensity, and confidence."""
        try:
            if not isinstance(text, str):
                raise InvalidInputError("Text must be a string")

            cleaned = text.strip()
            if not cleaned:
                raise InvalidInputError("Text cannot be empty")

            locale_emotion = load_locale("th")["emotion_service"]
            positive_keywords = locale_emotion["positive_keywords"]
            negative_keywords = locale_emotion["negative_keywords"]

            text_lower = cleaned.lower()

            if any(word in text_lower for word in positive_keywords):
                emotion = "joy"
                intensity = 7.0
            elif any(word in text_lower for word in negative_keywords):
                emotion = "sadness"
                intensity = 6.0
            else:
                emotion = "neutral"
                intensity = 5.0

            payload = {
                "emotion": emotion,
                "intensity": intensity,
                "confidence": 0.8,
                "raw_sentiment": emotion.upper(),
            }
            logger.info(
                "Emotion analyzed", extra={"emotion": emotion, "intensity": intensity}
            )
            return payload
        except InvalidInputError:
            raise
        except Exception as exc:  # noqa: BLE001 - wrap unexpected errors
            logger.error("Emotion analysis failed", exc_info=True)
            raise ServiceError(f"Emotion analysis failed: {exc}") from exc

    def detect_emotion_shift(
        self, previous_emotion: str, current_emotion: str
    ) -> Dict[str, object]:
        return {
            "from_emotion": previous_emotion,
            "to_emotion": current_emotion,
            "shift_type": "emotion_change",
            "positive_shift": current_emotion == "joy",
        }

    def generate_dharma_insight_from_emotion(
        self, emotion: str, intensity: float
    ) -> str:
        locale_emotion = load_locale("th")["emotion_service"]
        insights = locale_emotion["insights"]
        default_insight = locale_emotion["default_insight"]
        return insights.get(emotion.lower(), default_insight)


emotion_service = EmotionService()
