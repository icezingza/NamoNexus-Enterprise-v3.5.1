"""Integration tests for audio triage endpoint."""

from __future__ import annotations

import io
import os

import numpy as np
import soundfile as sf
import pytest
from fastapi.testclient import TestClient

from src.i18n import load_locale

TOKEN = os.getenv("NAMO_NEXUS_TOKEN")
if not TOKEN:
    pytest.skip("NAMO_NEXUS_TOKEN must be set for audio triage tests.", allow_module_level=True)
os.environ.setdefault("ENABLE_TRANSCRIPTION", "false")  # Disable Whisper for tests

from main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}
LOCALE = load_locale("th")


def create_test_wav(duration: float = 1.0, freq: float = 440.0) -> bytes:
    """Create a simple WAV file for testing."""
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    y = 0.3 * np.sin(2 * np.pi * freq * t).astype(np.float32)
    
    buffer = io.BytesIO()
    sf.write(buffer, y, sr, format='WAV')
    buffer.seek(0)
    return buffer.read()


class TestAudioTriageEndpoint:
    """Test cases for /triage/audio endpoint."""
    
    def test_audio_triage_success(self):
        """Test successful audio triage with valid WAV file."""
        audio_bytes = create_test_wav(duration=2.0)
        
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/wav")},
            data={
                "user_id": "audio_test_001",
                "message": LOCALE["tests"]["messages"]["audio_prompt"],
            },
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 200
        payload = response.json()
        assert "response" in payload
        assert "risk_level" in payload
        assert "multimodal_confidence" in payload
        assert "session_id" in payload
        # With voice features, confidence should be higher than text-only
        assert payload["multimodal_confidence"] >= 0.5
    
    def test_audio_triage_with_transcription_override(self):
        """Test audio triage with user-provided message overriding transcription."""
        audio_bytes = create_test_wav()
        custom_message = LOCALE["tests"]["messages"]["audio_custom"]
        
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/wav")},
            data={"user_id": "audio_test_002", "message": custom_message},
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 200
        payload = response.json()
        # Response should reflect the custom message context
        assert "response" in payload
    
    def test_audio_triage_no_auth(self):
        """Test audio triage without authentication fails."""
        audio_bytes = create_test_wav()
        
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/wav")},
            data={"user_id": "test"},
        )
        
        assert response.status_code in (401, 403)
    
    def test_audio_triage_invalid_format(self):
        """Test audio triage with invalid file format fails."""
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.txt", b"not audio data", "text/plain")},
            data={"user_id": "test"},
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 422
        assert "Only .wav / .mp3 allowed" in response.json()["detail"]
    
    def test_audio_triage_empty_file(self):
        """Test audio triage with empty file fails."""
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", b"", "audio/wav")},
            data={"user_id": "test"},
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 422
    
    def test_audio_triage_mp3_format(self):
        """Test audio triage accepts MP3 content type."""
        audio_bytes = create_test_wav()  # Still WAV data but testing content-type handling
        
        # Note: This tests content-type validation, not actual MP3 decoding
        # In real usage, librosa would handle the actual MP3 decoding
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/mpeg")},
            data={"user_id": "mp3_test"},
            headers=AUTH_HEADERS,
        )
        
        # Should accept the content type (actual decoding may fail for fake MP3)
        # We're testing the endpoint accepts MP3 content type
        assert response.status_code in (200, 400)  # 400 if decoding fails is acceptable
    
    def test_audio_triage_risk_detection(self):
        """Test that voice features contribute to risk assessment."""
        audio_bytes = create_test_wav()
        
        # Send with crisis keywords
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/wav")},
            data={
                "user_id": "crisis_test",
                "message": LOCALE["tests"]["messages"]["audio_crisis"],
            },
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 200
        payload = response.json()
        # Should detect severe risk from keywords
        assert payload["risk_level"] == "severe"
        assert payload["human_handoff_required"] is True


class TestAudioTriageFormValidation:
    """Test form field validation for audio triage."""
    
    def test_missing_user_id(self):
        """Test that user_id is required."""
        audio_bytes = create_test_wav()
        
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/wav")},
            data={},  # Missing user_id
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_audio_file(self):
        """Test that audio file is required."""
        response = client.post(
            "/triage/audio",
            data={"user_id": "test"},
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_optional_session_id(self):
        """Test that session_id is optional."""
        audio_bytes = create_test_wav()
        
        response = client.post(
            "/triage/audio",
            files={"audio": ("test.wav", audio_bytes, "audio/wav")},
            data={"user_id": "session_test"},  # No session_id
            headers=AUTH_HEADERS,
        )
        
        assert response.status_code == 200
        payload = response.json()
        assert "session_id" in payload
        assert payload["session_id"].startswith("session_")
