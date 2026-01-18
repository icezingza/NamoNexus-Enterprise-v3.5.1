# tests/test_dharma_service.py
"""
Unit tests for Dharma Service
"""

from src.i18n import load_locale
from src.services.dharma_service import dharma_service, DharmaAlignmentService


LOCALE = load_locale("th")
DHARMA = LOCALE["dharma_service"]


class TestDharmaService:
    """Test suite for DharmaAlignmentService"""

    def test_service_initialization(self):
        """Test service initializes correctly"""
        service = DharmaAlignmentService()
        assert service is not None
        assert len(service.four_noble_truths) == 4
        assert len(service.eightfold_path) == 8

    def test_apply_four_noble_truths_sadness(self):
        """Test Four Noble Truths analysis for sadness"""
        result = dharma_service.apply_four_noble_truths(
            problem="I feel sad about a project setback", emotion="sadness", intensity=7.5
        )

        # Check all stages present
        assert "dukkha" in result
        assert "samudaya" in result
        assert "nirodha" in result
        assert "magga" in result

        # Check dukkha stage
        assert "truth" in result["dukkha"]
        assert "validation" in result["dukkha"]
        assert "7.5" in result["dukkha"]["validation"]

        # Check samudaya stage
        assert result["samudaya"]["emotion"] == "sadness"
        assert len(result["samudaya"]["probable_causes"]) > 0

        # Check nirodha stage
        assert "truth" in result["nirodha"]
        assert "path_to_peace" in result["nirodha"]

        # Check magga stage
        assert "eightfold_path_steps" in result["magga"]
        assert len(result["magga"]["eightfold_path_steps"]) == 8

        # Check coherence score
        assert "coherence_score" in result
        assert 0 <= result["coherence_score"] <= 1

    def test_apply_four_noble_truths_anxiety(self):
        """Test Four Noble Truths analysis for anxiety"""
        result = dharma_service.apply_four_noble_truths(
            problem="I feel anxious about an exam", emotion="anxiety", intensity=6.0
        )

        assert result["samudaya"]["emotion"] == "anxiety"
        expected = DHARMA["cause_patterns"]["anxiety"]["likely_causes"][0]
        assert expected in result["samudaya"]["probable_causes"]
        assert len(result["magga"]["eightfold_path_steps"]) == 8

    def test_apply_four_noble_truths_anger(self):
        """Test Four Noble Truths analysis for anger"""
        result = dharma_service.apply_four_noble_truths(
            problem="I feel angry about unfair treatment", emotion="anger", intensity=8.0
        )

        assert result["samudaya"]["emotion"] == "anger"
        expected = DHARMA["cause_patterns"]["anger"]["likely_causes"][0]
        assert expected in result["samudaya"]["probable_causes"]
        assert len(result["magga"]["eightfold_path_steps"]) == 8

    def test_dharmic_path_high_intensity(self):
        """Test dharmic path suggestion for high intensity"""
        result = dharma_service.apply_four_noble_truths(
            problem="I am in deep pain", emotion="sadness", intensity=9.0
        )

        assert "dharmic_path" in result
        assert result["dharmic_path"] == DHARMA["path_messages"]["high"]

    def test_dharmic_path_medium_intensity(self):
        """Test dharmic path suggestion for medium intensity"""
        result = dharma_service.apply_four_noble_truths(
            problem="I feel low today", emotion="sadness", intensity=6.0
        )

        assert "dharmic_path" in result
        assert result["dharmic_path"] == DHARMA["path_messages"]["medium"]

    def test_dharmic_path_low_intensity(self):
        """Test dharmic path suggestion for low intensity"""
        result = dharma_service.apply_four_noble_truths(
            problem="I feel a bit bored", emotion="sadness", intensity=3.0
        )

        assert "dharmic_path" in result
        assert result["dharmic_path"] == DHARMA["path_messages"]["low"]

    def test_intensity_guidance_critical(self):
        """Test intensity guidance for critical level"""
        result = dharma_service.apply_four_noble_truths(
            problem="test", emotion="sadness", intensity=9.0
        )

        assert result["magga"]["intensity_guidance"] == DHARMA["intensity_guidance"]["high"]

    def test_intensity_guidance_medium(self):
        """Test intensity guidance for medium level"""
        result = dharma_service.apply_four_noble_truths(
            problem="test", emotion="sadness", intensity=6.0
        )

        assert result["magga"]["intensity_guidance"] == DHARMA["intensity_guidance"]["medium"]

    def test_intensity_guidance_low(self):
        """Test intensity guidance for low level"""
        result = dharma_service.apply_four_noble_truths(
            problem="test", emotion="sadness", intensity=2.0
        )

        assert result["magga"]["intensity_guidance"] == DHARMA["intensity_guidance"]["low"]

    def test_coherence_score_all_stages(self):
        """Test coherence score when all stages present"""
        result = dharma_service.apply_four_noble_truths(
            problem="test problem", emotion="sadness", intensity=5.0
        )

        # All stages should be present
        assert result["coherence_score"] == 0.95

    def test_unknown_emotion_fallback(self):
        """Test handling of unknown emotion"""
        result = dharma_service.apply_four_noble_truths(
            problem="test", emotion="unknown_emotion", intensity=5.0
        )

        # Should still return valid structure
        assert "dukkha" in result
        assert "samudaya" in result
        assert len(result["samudaya"]["probable_causes"]) > 0

    def test_empty_problem(self):
        """Test handling of empty problem"""
        result = dharma_service.apply_four_noble_truths(
            problem="", emotion="sadness", intensity=5.0
        )

        # Should still return valid structure
        assert "dukkha" in result
        assert result["coherence_score"] > 0

    def test_eightfold_path_included(self):
        """Test that eightfold path is included in response"""
        result = dharma_service.apply_four_noble_truths(
            problem="test", emotion="sadness", intensity=5.0
        )

        assert "eightfold_path" in result
        assert len(result["eightfold_path"]) == 8
        assert "Right View" in result["eightfold_path"]

    def test_thai_language_support(self):
        """Test Thai language in responses"""
        result = dharma_service.apply_four_noble_truths(
            problem="test", emotion="sadness", intensity=5.0
        )

        # Check Thai text present
        assert result["dukkha"]["truth"] == DHARMA["stages"]["dukkha"]["truth"]
        assert result["samudaya"]["truth"] == DHARMA["stages"]["samudaya"]["truth"]
        assert result["nirodha"]["truth"] == DHARMA["stages"]["nirodha"]["truth"]
        assert result["magga"]["truth"] == DHARMA["stages"]["magga"]["truth"]
