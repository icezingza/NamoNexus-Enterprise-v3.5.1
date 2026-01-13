from typing import Dict


class DharmaService:
    def apply_alignment_analysis(self, message: str, emotion: str, intensity: float) -> Dict[str, object]:
        stages = {
            "stage_1": "Identify the primary tension in the message.",
            "stage_2": "Trace likely drivers and constraints.",
            "stage_3": "Outline a stable resolution approach.",
            "stage_4": "Suggest a practical next action.",
        }
        path = "Stabilize input, reduce risk signals, then select a measured response."
        insight = "Focus on actionable steps that reduce uncertainty."
        confidence = round(min(1.0, 0.5 + (intensity / 20.0)), 2)
        return {
            "stages": stages,
            "path": path,
            "insight": insight,
            "confidence": confidence,
            "emotion": emotion,
        }

    def apply_four_stage_analysis(self, message: str, emotion: str, intensity: float) -> Dict[str, object]:
        return self.apply_alignment_analysis(message, emotion, intensity)


dharma_service = DharmaService()
