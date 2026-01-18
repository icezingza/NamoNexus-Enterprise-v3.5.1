# src/services/dharma_service.py
"""
Dharma Alignment Service - Four Noble Truths Framework
Provides wisdom-based emotional support through Buddhist principles
"""

from typing import Dict
from enum import Enum

from src.i18n import load_locale


_LOCALE = load_locale("th")


class DharmaStage(str, Enum):
    """Four Noble Truths Stages"""

    DUKKHA = "dukkha"  # Suffering/Problem identification
    SAMUDAYA = "samudaya"  # Origin/Root cause analysis
    NIRODHA = "nirodha"  # Cessation/Solution emergence
    MAGGA = "magga"  # Path/Implementation strategy


class DharmaAlignmentService:
    """
    Four-stage Dharma alignment analysis engine.
    Core insight: Problems have roots, solutions have paths
    """

    def __init__(self):
        self.locale = _LOCALE["dharma_service"]
        self.four_noble_truths = self.locale["four_noble_truths"]
        self.eightfold_path = self.locale["eightfold_path"]
        self._stages = self.locale["stages"]
        self._cause_patterns = self.locale["cause_patterns"]
        self._default_cause_pattern = self.locale["default_cause_pattern"]
        self._practical_steps = self.locale["practical_steps"]
        self._fallback_steps = self.locale["fallback_steps"]
        self._path_messages = self.locale["path_messages"]
        self._intensity_guidance = self.locale["intensity_guidance"]

    def apply_four_noble_truths(
        self, problem: str, emotion: str, intensity: float
    ) -> Dict:
        """
        Apply Four Noble Truths framework to user's problem

        Args:
            problem: User's problem statement
            emotion: Detected emotion (sadness, anxiety, anger, etc.)
            intensity: Emotional intensity (0-10)

        Returns:
            Complete four-stage analysis with wisdom insights
        """

        # STAGE 1: DUKKHA - Validate the suffering
        stage_1 = self._analyze_dukkha(problem, intensity)

        # STAGE 2: SAMUDAYA - Find root causes
        stage_2 = self._analyze_samudaya(problem, emotion)

        # STAGE 3: NIRODHA - Show the way to release
        stage_3 = self._analyze_nirodha(problem)

        # STAGE 4: MAGGA - Provide practical steps
        stage_4 = self._analyze_magga(emotion, intensity)

        return {
            "dukkha": stage_1,
            "samudaya": stage_2,
            "nirodha": stage_3,
            "magga": stage_4,
            "eightfold_path": self.eightfold_path,
            "dharmic_path": self._suggest_dharmic_path(emotion, intensity),
            "coherence_score": self._compute_coherence(
                stage_1, stage_2, stage_3, stage_4
            ),
        }

    def _analyze_dukkha(self, problem: str, intensity: float) -> Dict:
        """
        STAGE 1: Suffering validation
        Key: "Your pain is real. That's valid."
        """
        stage = self._stages["dukkha"]
        return {
            "truth": stage["truth"],
            "validation": stage["validation"].format(intensity=intensity),
            "insight": stage["insight"],
            "reflection": stage["reflection"],
        }

    def _analyze_samudaya(self, problem: str, emotion: str) -> Dict:
        """
        STAGE 2: Root cause analysis
        Key: "Let's understand what's actually causing this"
        """

        pattern = self._cause_patterns.get(
            emotion.lower(),
            self._default_cause_pattern,
        )
        stage = self._stages["samudaya"]

        return {
            "truth": stage["truth"],
            "emotion": emotion,
            "probable_causes": pattern["likely_causes"],
            "deeper_insight": pattern["insight"],
            "deeper_question": stage["deeper_question"],
        }

    def _analyze_nirodha(self, problem: str) -> Dict:
        """
        STAGE 3: Cessation or release
        Key: "This can change. Not by avoiding, but by understanding"
        """
        stage = self._stages["nirodha"]
        return {
            "truth": stage["truth"],
            "path_to_peace": stage["path_to_peace"],
            "liberating_insight": stage["liberating_insight"],
            "perspective": stage["perspective"],
            "future_state": stage["future_state"],
        }

    def _analyze_magga(self, emotion: str, intensity: float) -> Dict:
        """
        STAGE 4: The path forward
        Key: "Here are 8 dimensions to cultivate wisdom"
        """

        steps = self._practical_steps.get(emotion.lower(), self._fallback_steps)
        stage = self._stages["magga"]
        fallback_step = self._fallback_steps[0] if self._fallback_steps else ""

        return {
            "truth": stage["truth"],
            "eightfold_path_steps": steps,
            "immediate_action": stage["immediate_action_format"].format(
                step=steps[0] if steps else fallback_step
            ),
            "intensity_guidance": self._get_intensity_guidance(intensity),
        }

    def _suggest_dharmic_path(self, emotion: str, intensity: float) -> str:
        """
        Generate wisdom message based on emotion intensity
        """
        if intensity > 8:
            return self._path_messages["high"]
        elif intensity > 5:
            return self._path_messages["medium"]
        else:
            return self._path_messages["low"]

    def _get_intensity_guidance(self, intensity: float) -> str:
        """Guidance based on emotional intensity"""
        if intensity > 8:
            return self._intensity_guidance["high"]
        elif intensity > 5:
            return self._intensity_guidance["medium"]
        else:
            return self._intensity_guidance["low"]

    def _compute_coherence(self, s1: Dict, s2: Dict, s3: Dict, s4: Dict) -> float:
        """
        Calculate coherence score (0-1)
        Shows how well the four stages align together
        """
        # Simple model: all stages present = high coherence
        all_stages_present = all([s1, s2, s3, s4])
        return 0.95 if all_stages_present else 0.75


# Singleton instance
dharma_service = DharmaAlignmentService()
