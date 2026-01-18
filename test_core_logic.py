import pytest
import sys
import os
import asyncio

# Ensure project root is in path so we can import core_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core_engine import MultiModalTriageEngine, EthicalCalibrationKernel
# Import MultiModalAnalysis from core_engine (where it is imported from models)
from core_engine import MultiModalAnalysis

class TestCoreEngine:
    """Tests for MultiModalTriageEngine and EthicalCalibrationKernel"""

    @pytest.fixture
    def triage_engine(self):
        return MultiModalTriageEngine()

    @pytest.fixture
    def ethics_kernel(self):
        return EthicalCalibrationKernel()

    @pytest.mark.asyncio
    async def test_analyze_text_risk(self, triage_engine):
        """Test text analysis logic from core_engine"""
        # Test high risk keywords (assuming default config contains 'die')
        # Note: Actual keywords depend on src.i18n config, assuming standard set
        risk = await triage_engine.analyze_text("I want to die")
        assert risk > 0.1, "Should detect risk in crisis message"

        # Test low risk
        risk = await triage_engine.analyze_text("I am happy today")
        assert risk < 0.5, "Should detect low risk for positive message"

    @pytest.mark.asyncio
    async def test_multimodal_fusion(self, triage_engine):
        """Test fusion of text, voice, and facial data"""
        text = "I feel tired"
        # Voice features: low energy (< 0.2) adds 0.5 risk
        voice = {"energy": 0.1, "pitch_variance": 0.9} 
        # Facial features: inner brow raise (0.8 * 0.4 = 0.32 risk component)
        face = {"au1": 0.8} 

        result = await triage_engine.multimodal_fusion(text, voice, face)
        
        assert isinstance(result, MultiModalAnalysis)
        assert result.combined_risk > 0.0
        assert result.voice_stress > 0.0
        assert result.facial_distress > 0.0

    @pytest.mark.asyncio
    async def test_ethics_calibration(self, ethics_kernel):
        """Test ethical calibration and safety checks"""
        # Mock a high risk analysis
        mock_analysis = MultiModalAnalysis(
            text_risk=0.9, voice_stress=0.0, facial_distress=0.0,
            combined_risk=0.9, confidence=1.0,
            text_confidence=1.0, voice_confidence=0.0, facial_confidence=0.0,
            risk_factors=[]
        )
        
        # "kill myself" should trigger immediate escalation in check_safety
        text = "I want to kill myself"
        result = await ethics_kernel.calibrate(text, mock_analysis)
        
        assert result['risk_level'] == 'severe'
        assert result['requires_human'] is True
        assert result['intervention'] == 'compassionate_support'

    @pytest.mark.asyncio
    async def test_dharma_alignment(self, ethics_kernel):
        """Test Dharma principle detection"""
        text = "I am trying to be mindful"
        dharma = ethics_kernel.lake.calculate_dharma_alignment(text)
        assert "dharma_score" in dharma
        assert isinstance(dharma["dharma_score"], float)