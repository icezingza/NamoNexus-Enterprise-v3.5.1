from typing import Dict, List


class PersonalizationEngine:
    def __init__(self) -> None:
        self.templates = {
            "joy": "I'm glad to hear that. Want to share more about what went well?",
            "sadness": "I'm here with you. Do you want to talk about what's weighing on you?",
            "anger": "That sounds intense. Let's slow it down and unpack what happened.",
            "anxiety": "That sounds stressful. Would it help to name the biggest worry?",
            "neutral": "I'm listening. Tell me a bit more about what's on your mind.",
        }
        self.recommendations = {
            "joy": ["Celebrate small wins", "Note what helped today"],
            "sadness": ["Take a slow breath", "Reach out to someone you trust"],
            "anger": ["Pause before responding", "Identify the boundary that felt crossed"],
            "anxiety": ["List what you can control", "Focus on the next small step"],
            "neutral": ["Share more context", "Highlight what matters most"],
        }

    def generate_personalized_response(self, user_id: str, emotion: str, message: str) -> Dict[str, object]:
        template = self.templates.get(emotion, self.templates["neutral"])
        recommendations = self.recommendations.get(emotion, self.recommendations["neutral"])
        response = template.format(user_id=user_id, message=message)
        return {
            "personalized_response": response,
            "recommendations": recommendations,
        }


personalization_engine = PersonalizationEngine()
