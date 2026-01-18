from typing import Dict, Any

from src.i18n import load_locale


_LOCALE = load_locale("th")


class EmotionAnalyzer:
    """Simple placeholder emotion analyzer."""

    def analyze(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        lowered = text.lower()
        valence = -0.3 if any(w in lowered for w in ["sad", "tired", "empty", "alone"]) else 0.1
        distress_triggers = _LOCALE["namo_nexus"]["emotion_analyzer"]["distress_triggers"]
        distress_level = "high" if any(trigger in lowered for trigger in distress_triggers) else "low"

        return {
            "valence": valence,
            "arousal": 0.4,
            "distress_level": distress_level,
            "confidence": 0.6,
        }
