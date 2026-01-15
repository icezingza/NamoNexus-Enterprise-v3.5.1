"""Tests for voice feature extraction."""

from __future__ import annotations

import io
from unittest.mock import patch

import numpy as np
import pytest
import soundfile as sf

from voice_extractor import VoiceExtractor, VoiceAnalysisResult, calculate_voice_stress_score


def generate_test_audio(
    duration: float = 2.0,
    freq: float = 440.0,
    sample_rate: int = 16000,
) -> bytes:
    """Generate a simple sine wave audio for testing.
    
    Creates a tone with some variation to simulate speech-like audio.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Create a tone with harmonics and slight variation
    y = 0.3 * np.sin(2 * np.pi * freq * t)
    y += 0.1 * np.sin(2 * np.pi * (freq * 1.5) * t)  # harmonic
    y += 0.05 * np.sin(2 * np.pi * (freq * 0.5) * t)  # sub-harmonic
    # Add amplitude modulation to simulate speech patterns
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)  # 3Hz modulation
    y = (y * envelope).astype(np.float32)
    
    buffer = io.BytesIO()
    sf.write(buffer, y, sample_rate, format='WAV')
    buffer.seek(0)
    return buffer.read()


def generate_silent_audio(duration: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generate silent audio for testing edge cases."""
    y = np.zeros(int(sample_rate * duration), dtype=np.float32)
    buffer = io.BytesIO()
    sf.write(buffer, y, sample_rate, format='WAV')
    buffer.seek(0)
    return buffer.read()


class TestVoiceExtractor:
    """Test cases for VoiceExtractor class."""
    
    def test_extract_from_bytes_basic(self):
        """Test basic extraction from audio bytes."""
        extractor = VoiceExtractor(enable_transcription=False)
        audio_bytes = generate_test_audio()
        
        result = extractor.extract_from_bytes(audio_bytes)
        
        assert isinstance(result, VoiceAnalysisResult)
        assert 0 <= result.pitch_variance <= 1
        assert 0 <= result.energy <= 1
        assert 0 <= result.speech_rate <= 1
        assert 0 <= result.pause_ratio <= 1
        assert 0 <= result.tremor_index <= 1
        assert result.duration_seconds > 0
    
    def test_extract_returns_valid_pitch(self):
        """Test that pitch values are reasonable."""
        extractor = VoiceExtractor(enable_transcription=False)
        audio_bytes = generate_test_audio(freq=300.0)  # 300Hz tone
        
        result = extractor.extract_from_bytes(audio_bytes)
        
        # Pitch should be detected
        assert result.pitch_mean_hz > 0
        # Pitch variance should be low for pure tone
        assert result.pitch_variance < 0.5
    
    def test_extract_handles_short_audio(self):
        """Test handling of very short audio."""
        extractor = VoiceExtractor(enable_transcription=False)
        audio_bytes = generate_test_audio(duration=0.3)  # Very short
        
        result = extractor.extract_from_bytes(audio_bytes)
        
        assert isinstance(result, VoiceAnalysisResult)
        # Should still return valid values
        assert result.duration_seconds < 1.0
    
    def test_extract_handles_silent_audio(self):
        """Test handling of silent audio."""
        extractor = VoiceExtractor(enable_transcription=False)
        audio_bytes = generate_silent_audio()
        
        result = extractor.extract_from_bytes(audio_bytes)
        
        assert isinstance(result, VoiceAnalysisResult)
        assert result.energy < 0.1  # Should be very low
        assert result.pause_ratio > 0.8  # Should be mostly silence
    
    def test_to_voice_features_dict_format(self):
        """Test that to_voice_features_dict returns expected format."""
        extractor = VoiceExtractor(enable_transcription=False)
        audio_bytes = generate_test_audio()
        
        result = extractor.extract_from_bytes(audio_bytes)
        features_dict = result.to_voice_features_dict()
        
        assert "pitch_variance" in features_dict
        assert "speech_rate" in features_dict
        assert "energy" in features_dict
        assert len(features_dict) == 3
    
    def test_to_full_dict_format(self):
        """Test that to_full_dict returns all fields."""
        extractor = VoiceExtractor(enable_transcription=False)
        audio_bytes = generate_test_audio()
        
        result = extractor.extract_from_bytes(audio_bytes)
        full_dict = result.to_full_dict()
        
        expected_keys = {
            "pitch_variance", "energy", "speech_rate",
            "pause_ratio", "tremor_index", "pitch_mean_hz",
            "duration_seconds", "transcription", "transcription_language",
        }
        assert set(full_dict.keys()) == expected_keys


class TestVoiceStressScore:
    """Test cases for stress score calculation."""
    
    def test_low_energy_increases_stress(self):
        """Test that low energy contributes to higher stress score."""
        low_energy = VoiceAnalysisResult(
            pitch_variance=0.5, energy=0.1, speech_rate=0.5,
            pause_ratio=0.3, tremor_index=0.0,
            pitch_mean_hz=200, duration_seconds=5.0,
        )
        high_energy = VoiceAnalysisResult(
            pitch_variance=0.5, energy=0.9, speech_rate=0.5,
            pause_ratio=0.3, tremor_index=0.0,
            pitch_mean_hz=200, duration_seconds=5.0,
        )
        
        low_score = calculate_voice_stress_score(low_energy)
        high_score = calculate_voice_stress_score(high_energy)
        
        assert low_score > high_score
    
    def test_flat_affect_increases_stress(self):
        """Test that low pitch variance (flat affect) increases stress score."""
        flat = VoiceAnalysisResult(
            pitch_variance=0.1, energy=0.5, speech_rate=0.5,
            pause_ratio=0.3, tremor_index=0.0,
            pitch_mean_hz=200, duration_seconds=5.0,
        )
        varied = VoiceAnalysisResult(
            pitch_variance=0.9, energy=0.5, speech_rate=0.5,
            pause_ratio=0.3, tremor_index=0.0,
            pitch_mean_hz=200, duration_seconds=5.0,
        )
        
        flat_score = calculate_voice_stress_score(flat)
        varied_score = calculate_voice_stress_score(varied)
        
        assert flat_score > varied_score
    
    def test_tremor_increases_stress(self):
        """Test that voice tremor increases stress score."""
        tremor = VoiceAnalysisResult(
            pitch_variance=0.5, energy=0.5, speech_rate=0.5,
            pause_ratio=0.3, tremor_index=0.9,
            pitch_mean_hz=200, duration_seconds=5.0,
        )
        no_tremor = VoiceAnalysisResult(
            pitch_variance=0.5, energy=0.5, speech_rate=0.5,
            pause_ratio=0.3, tremor_index=0.0,
            pitch_mean_hz=200, duration_seconds=5.0,
        )
        
        tremor_score = calculate_voice_stress_score(tremor)
        no_tremor_score = calculate_voice_stress_score(no_tremor)
        
        assert tremor_score > no_tremor_score
    
    def test_stress_score_bounded(self):
        """Test that stress score is always between 0 and 1."""
        # Extreme case: all indicators suggest distress
        extreme = VoiceAnalysisResult(
            pitch_variance=0.0, energy=0.0, speech_rate=0.0,
            pause_ratio=1.0, tremor_index=1.0,
            pitch_mean_hz=0, duration_seconds=1.0,
        )
        
        score = calculate_voice_stress_score(extreme)
        
        assert 0 <= score <= 1
