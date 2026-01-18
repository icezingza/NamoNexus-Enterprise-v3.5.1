from typing import Dict

from src.i18n import load_locale


_LOCALE = load_locale("th")


class EmotionService:
    def __init__(self) -> None:
        pass

    def analyze_sentiment(self, text: str) -> Dict:
        locale_emotion = _LOCALE["emotion_service_basic"]
        positive_keywords = locale_emotion["positive_keywords"]
        negative_keywords = locale_emotion["negative_keywords"]

        text_lower = text.lower()

        if any(word in text_lower for word in positive_keywords):
            emotion = "joy"
            intensity = 7.0
        elif any(word in text_lower for word in negative_keywords):
            emotion = "sadness"
            intensity = 6.0
        else:
            emotion = "neutral"
            intensity = 5.0

        return {
            "emotion": emotion,
            "intensity": intensity,
            "confidence": 0.8,
            "raw_sentiment": emotion.upper(),
        }

    def detect_emotion_shift(self, previous_emotion: str, current_emotion: str) -> Dict:
        return {
            "from_emotion": previous_emotion,
            "to_emotion": current_emotion,
            "shift_type": "emotion_change",
            "positive_shift": current_emotion == "joy",
        }

    def generate_dharma_insight_from_emotion(self, emotion: str, intensity: float) -> str:
        locale_emotion = _LOCALE["emotion_service_basic"]
        insights = locale_emotion["insights"]
        default_insight = locale_emotion["default_insight"]
        return insights.get(emotion.lower(), default_insight)


emotion_service = EmotionService()
