"""Voice feature extraction service using librosa and Whisper.

This module provides voice analysis capabilities for mental health triage,
extracting acoustic features that correlate with emotional distress:
- Pitch variance (flat affect indicator)
- Energy levels (fatigue/distress indicator)
- Speech rate (depression/anxiety indicator)
- Pause patterns (hesitation/cognitive load indicator)
- Voice tremor (fear/stress indicator)

Optionally transcribes audio to text using OpenAI Whisper.
"""

from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple

logger = logging.getLogger("namo_nexus.voice")

# Graceful degradation for Librosa/Numpy (Fix for Windows/Python 3.13 issues)
try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except (ImportError, OSError, RuntimeError) as e:
    logger.error(f"Audio processing libraries (Librosa/Numpy) not available: {e}")
    LIBROSA_AVAILABLE = False
    # Mock np for type hints to prevent NameError
    class MockNp:
        ndarray = list
    np = MockNp()


# Whisper is optional - will gracefully degrade if not available
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not installed. Speech-to-text will be disabled.")


@dataclass
class VoiceAnalysisResult:
    """Result of voice feature extraction."""
    
    # Core features for triage (normalized 0-1)
    pitch_variance: float
    energy: float
    speech_rate: float
    pause_ratio: float
    tremor_index: float
    
    # Metadata
    pitch_mean_hz: float
    duration_seconds: float
    
    # Optional transcription
    transcription: Optional[str] = None
    transcription_language: Optional[str] = None
    
    def to_voice_features_dict(self) -> dict:
        """Convert to format expected by TriageRequest.voice_features."""
        return {
            "pitch_variance": self.pitch_variance,
            "speech_rate": self.speech_rate,
            "energy": self.energy,
        }
    
    def to_full_dict(self) -> dict:
        """Return all features for logging/debugging."""
        return {
            "pitch_variance": self.pitch_variance,
            "energy": self.energy,
            "speech_rate": self.speech_rate,
            "pause_ratio": self.pause_ratio,
            "tremor_index": self.tremor_index,
            "pitch_mean_hz": self.pitch_mean_hz,
            "duration_seconds": self.duration_seconds,
            "transcription": self.transcription,
            "transcription_language": self.transcription_language,
        }


class VoiceExtractor:
    """Extract emotional indicators from audio.
    
    This class analyzes audio recordings to extract features that may indicate
    emotional distress, particularly useful for mental health triage systems.
    
    Features extracted:
    - pitch_variance: Low variance (flat affect) can indicate depression
    - energy: Low energy can indicate fatigue or hopelessness
    - speech_rate: Slow speech can indicate depression; fast speech can indicate anxiety
    - pause_ratio: High pause ratio can indicate cognitive load or hesitation
    - tremor_index: Voice tremor can indicate fear or extreme stress
    
    Optionally uses OpenAI Whisper for speech-to-text transcription.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        whisper_model: str = "base",
        enable_transcription: bool = True,
    ) -> None:
        """Initialize the voice extractor.
        
        Args:
            sample_rate: Target sample rate for audio processing (default 16kHz)
            whisper_model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            enable_transcription: Whether to enable speech-to-text
        """
        self.sample_rate = sample_rate
        self.enable_transcription = enable_transcription and WHISPER_AVAILABLE
        self._whisper_model = None
        self._whisper_model_name = whisper_model
    
    def _get_whisper_model(self):
        """Lazy load Whisper model."""
        if self._whisper_model is None and self.enable_transcription:
            logger.info(f"Loading Whisper model: {self._whisper_model_name}")
            self._whisper_model = whisper.load_model(self._whisper_model_name)
        return self._whisper_model
    
    def extract_from_bytes(
        self,
        audio_bytes: bytes,
        transcribe: bool = True,
    ) -> VoiceAnalysisResult:
        """Extract features from audio bytes.
        
        Args:
            audio_bytes: Raw audio file bytes (WAV, MP3, etc.)
            transcribe: Whether to transcribe audio to text
            
        Returns:
            VoiceAnalysisResult with extracted features
        """
        if not LIBROSA_AVAILABLE:
            logger.warning("Librosa unavailable. Returning dummy voice features.")
            return VoiceAnalysisResult(
                pitch_variance=0.5,
                energy=0.5,
                speech_rate=0.5,
                pause_ratio=0.0,
                tremor_index=0.0,
                pitch_mean_hz=0.0,
                duration_seconds=1.0,
                transcription="[Audio analysis unavailable - Librosa missing]"
            )

        # Load audio with librosa
        try:
            y, sr = librosa.load(
                io.BytesIO(audio_bytes),
                sr=self.sample_rate,
                mono=True,
            )
            
            # Extract acoustic features
            result = self._analyze_audio(y, sr)
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return VoiceAnalysisResult(
                pitch_variance=0.5,
                energy=0.5,
                speech_rate=0.5,
                pause_ratio=0.0,
                tremor_index=0.0,
                pitch_mean_hz=0.0,
                duration_seconds=1.0,
                transcription=f"[Audio analysis failed: {e}]"
            )
        
        # Optionally transcribe
        if transcribe and self.enable_transcription:
            try:
                text, lang = self._transcribe(y)
                result.transcription = text
                result.transcription_language = lang
            except Exception as e:
                logger.warning(f"Transcription failed: {e}")
        
        return result
    
    def extract_from_file(
        self,
        file_path: str,
        transcribe: bool = True,
    ) -> VoiceAnalysisResult:
        """Extract features from audio file path.
        
        Args:
            file_path: Path to audio file
            transcribe: Whether to transcribe audio to text
            
        Returns:
            VoiceAnalysisResult with extracted features
        """
        if not LIBROSA_AVAILABLE:
            logger.warning("Librosa unavailable. Returning dummy voice features.")
            return VoiceAnalysisResult(
                pitch_variance=0.5,
                energy=0.5,
                speech_rate=0.5,
                pause_ratio=0.0,
                tremor_index=0.0,
                pitch_mean_hz=0.0,
                duration_seconds=1.0,
                transcription="[Audio analysis unavailable - Librosa missing]"
            )

        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            result = self._analyze_audio(y, sr)
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return VoiceAnalysisResult(
                pitch_variance=0.5,
                energy=0.5,
                speech_rate=0.5,
                pause_ratio=0.0,
                tremor_index=0.0,
                pitch_mean_hz=0.0,
                duration_seconds=1.0,
                transcription=f"[Audio analysis failed: {e}]"
            )
        
        if transcribe and self.enable_transcription:
            try:
                text, lang = self._transcribe(y)
                result.transcription = text
                result.transcription_language = lang
            except Exception as e:
                logger.warning(f"Transcription failed: {e}")
        
        return result
    
    def _analyze_audio(self, y: np.ndarray, sr: int) -> VoiceAnalysisResult:
        """Core audio analysis logic.
        
        Args:
            y: Audio time series (mono)
            sr: Sample rate
            
        Returns:
            VoiceAnalysisResult with acoustic features
        """
        duration = len(y) / sr
        
        # Handle very short or silent audio
        if duration < 0.5 or np.max(np.abs(y)) < 0.001:
            return VoiceAnalysisResult(
                pitch_variance=0.5,
                energy=0.0,
                speech_rate=0.5,
                pause_ratio=1.0,
                tremor_index=0.0,
                pitch_mean_hz=0.0,
                duration_seconds=duration,
            )
        
        # Pitch analysis using piptrack
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[pitches > 0]
        
        if len(pitch_values) > 0:
            pitch_mean = float(np.mean(pitch_values))
            pitch_std = float(np.std(pitch_values))
            # Normalize variance: typical range 0-200 Hz std -> 0-1
            pitch_variance = min(pitch_std / 200.0, 1.0)
        else:
            pitch_mean = 0.0
            pitch_variance = 0.5  # Default to neutral
        
        # Energy analysis (RMS)
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = float(np.mean(rms))
        # Normalize: typical voice RMS 0.01-0.1 -> 0-1
        energy = min(energy_mean * 10, 1.0)
        
        # Speech rate via onset detection
        # More onsets per second = faster speech
        onsets = librosa.onset.onset_detect(y=y, sr=sr)
        onsets_per_second = len(onsets) / duration if duration > 0 else 0
        # Typical speech: 2-6 syllables per second
        speech_rate = min(onsets_per_second / 6.0, 1.0)
        
        # Pause analysis
        silence_threshold = 0.02
        silent_frames = np.sum(rms < silence_threshold)
        pause_ratio = float(silent_frames / len(rms)) if len(rms) > 0 else 0.0
        
        # Tremor detection (short-term pitch instability)
        tremor_index = self._detect_tremor(pitch_values)
        
        return VoiceAnalysisResult(
            pitch_variance=pitch_variance,
            energy=energy,
            speech_rate=speech_rate,
            pause_ratio=pause_ratio,
            tremor_index=tremor_index,
            pitch_mean_hz=pitch_mean,
            duration_seconds=duration,
        )
    
    def _detect_tremor(self, pitch_values: np.ndarray) -> float:
        """Detect voice tremor from short-term pitch instability.
        
        Voice tremor (shakiness) can indicate fear, stress, or crying.
        We measure this by looking at rapid pitch fluctuations.
        
        Args:
            pitch_values: Array of pitch values (Hz)
            
        Returns:
            Tremor index normalized to 0-1
        """
        if len(pitch_values) < 20:
            return 0.0
        
        # Calculate local variance in short windows
        window_size = min(10, len(pitch_values) // 5)
        if window_size < 3:
            return 0.0
        
        local_vars = []
        for i in range(0, len(pitch_values) - window_size, window_size // 2):
            window = pitch_values[i:i + window_size]
            if len(window) > 1:
                local_vars.append(np.std(window))
        
        if not local_vars:
            return 0.0
        
        # High local variance = tremor
        # Normalize: typical tremor std 10-50 Hz -> 0-1
        mean_local_var = float(np.mean(local_vars))
        return min(mean_local_var / 50.0, 1.0)
    
    def _transcribe(self, y: np.ndarray) -> Tuple[str, str]:
        """Transcribe audio using Whisper.
        
        Args:
            y: Audio time series (must be 16kHz mono)
            
        Returns:
            Tuple of (transcription text, detected language)
        """
        model = self._get_whisper_model()
        if model is None:
            return "", ""
        
        # Whisper expects float32 audio
        audio = y.astype(np.float32)
        
        # Transcribe with automatic language detection
        result = model.transcribe(
            audio,
            language=None,  # Auto-detect
            task="transcribe",
        )
        
        text = result.get("text", "").strip()
        language = result.get("language", "unknown")
        
        return text, language


def calculate_voice_stress_score(features: VoiceAnalysisResult) -> float:
    """Calculate overall stress/risk score from voice features.
    
    This function combines multiple voice features into a single stress score
    that can be used for mental health triage.
    
    Signs of distress (higher score):
    - Low energy (fatigue, hopelessness)
    - Low pitch variance (flat affect, common in depression)
    - Slow speech (psychomotor retardation)
    - High pause ratio (cognitive difficulties, hesitation)
    - High tremor (fear, crying, extreme stress)
    
    Args:
        features: VoiceAnalysisResult from voice extraction
        
    Returns:
        Stress score from 0.0 (calm) to 1.0 (high distress)
    """
    weights = {
        "low_energy": 0.20,
        "low_variance": 0.25,  # Flat affect is strong indicator
        "slow_speech": 0.20,
        "high_pause": 0.15,
        "tremor": 0.20,
    }
    
    stress_score = 0.0
    
    # Low energy indicates fatigue/hopelessness
    stress_score += (1 - features.energy) * weights["low_energy"]
    
    # Low pitch variance (flat affect) indicates depression
    stress_score += (1 - features.pitch_variance) * weights["low_variance"]
    
    # Slow speech indicates psychomotor retardation
    stress_score += (1 - features.speech_rate) * weights["slow_speech"]
    
    # High pause ratio indicates cognitive difficulties
    stress_score += features.pause_ratio * weights["high_pause"]
    
    # Tremor indicates fear/stress
    stress_score += features.tremor_index * weights["tremor"]
    
    return min(stress_score, 1.0)


# Configuration from environment
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
ENABLE_TRANSCRIPTION = os.getenv("ENABLE_TRANSCRIPTION", "true").lower() == "true"

# Singleton instance
voice_extractor = VoiceExtractor(
    whisper_model=WHISPER_MODEL,
    enable_transcription=ENABLE_TRANSCRIPTION,
)
