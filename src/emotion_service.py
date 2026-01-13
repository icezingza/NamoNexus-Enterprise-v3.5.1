from typing import Dict


class EmotionService:
    def __init__(self) -> None:
        pass

    def analyze_sentiment(self, text: str) -> Dict:
        positive_keywords = ["ดี", "ดีใจ", "สุข", "ยินดี", "ชอบ"]
        negative_keywords = ["เศร้า", "เหงา", "กังวล", "โกรธ", "หนาว"]

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
        insights = {
            "sadness": "ทุกข์นี้ไม่เที่ยง... มันจะเปลี่ยนแปลง",
            "anxiety": "ความกังวลเกิดจากอนาคต... ปัจจุบันนี้ปลอดภัย",
            "anger": "โครธคือสัญญาณที่บอกว่ามีขอบเขตถูกลั่วง",
            "joy": "ความสุขชั่วขณะ... ซาบซึ้งด้วยสติ",
        }
        return insights.get(emotion.lower(), "ทุกอารมณ์คือข้อมูล ไม่ใช่ความจริง")


emotion_service = EmotionService()
