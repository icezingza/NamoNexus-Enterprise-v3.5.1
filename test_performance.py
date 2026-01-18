import pytest
import time
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core_engine import MultiModalTriageEngine

class TestPerformance:
    """Performance dimension testing"""

    @pytest.fixture
    def engine(self):
        return MultiModalTriageEngine()

    @pytest.mark.asyncio
    async def test_text_analysis_latency(self, engine):
        """Ensure text analysis is under 50ms for standard input"""
        text = "I am feeling a bit stressed but I will be okay."
        
        start_time = time.perf_counter()
        await engine.analyze_text(text)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        print(f"\nText Analysis Latency: {duration_ms:.2f}ms")
        
        # Threshold: 50ms (Python is fast enough for rule-based/light ML)
        assert duration_ms < 50, f"Text analysis too slow: {duration_ms}ms"

    @pytest.mark.asyncio
    async def test_multimodal_fusion_latency(self, engine):
        """Ensure full fusion is under 100ms"""
        text = "I don't know what to do."
        voice = {"energy": 0.3, "pitch_variance": 0.5}
        face = {"au1": 0.5}

        start_time = time.perf_counter()
        await engine.multimodal_fusion(text, voice, face)
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000
        print(f"\nFusion Latency: {duration_ms:.2f}ms")
        assert duration_ms < 100, f"Fusion too slow: {duration_ms}ms"