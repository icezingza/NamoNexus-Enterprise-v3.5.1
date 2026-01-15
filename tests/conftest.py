import asyncio
import json
import os
import sys
import typing
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("NAMO_NEXUS_TOKEN", "test-token")

from main import app

AUTH_TOKEN = os.environ["NAMO_NEXUS_TOKEN"]

# Compatibility patch for Pydantic with Python 3.13+
# Pydantic versions < 2.10 (approx) call typing._eval_type with 'prefer_fwd_module'
# which causes a TypeError in newer Python versions.
if sys.version_info >= (3, 13) and hasattr(typing, "_eval_type"):
    _original_eval_type = typing._eval_type

    def _patched_eval_type(t, globalns, localns, type_params=None, **kwargs):
        # Remove 'prefer_fwd_module' if present, as it's not supported in this Python version's typing._eval_type
        kwargs.pop('prefer_fwd_module', None)
        return _original_eval_type(t, globalns, localns, type_params=type_params, **kwargs)

    typing._eval_type = _patched_eval_type


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_user_message():
    """Sample user message for testing."""
    return {
        "user_id": "test_user_123",
        "message": "I am feeling anxious about my job",
    }


@pytest.fixture
def sample_reflect_request():
    """Sample reflect request."""
    return {
        "user_id": "test_user_456",
        "message": "I feel calm and peaceful today",
    }


@pytest.fixture
def auth_headers():
    """Authorization headers for secured endpoints."""
    return {"Authorization": f"Bearer {AUTH_TOKEN}"}


@pytest.fixture
def mock_emotion_analyzer():
    """Mock emotion analyzer."""
    mock = Mock()
    mock.reflect.return_value = Mock(
        response_text="You are safe",
        emotional_matching_score=0.85,
        support_level="High",
    )
    return mock


@pytest.fixture
def mock_safety_shield():
    """Mock safety shield."""
    mock = Mock()
    mock.protect.return_value = Mock(
        is_safe=True,
        risk_level=0.0,
        reason=None,
    )
    return mock


@pytest.fixture
def mock_persona_core():
    """Mock persona core."""
    mock = AsyncMock()
    mock.process.return_value = {
        "reflection_text": "I hear your concerns",
        "tone": "compassionate",
        "coherence": 0.85,
        "moral_index": 0.80,
        "memory_summary": "User anxious about work",
        "dhamma_tags": ["compassion"],
        "process_time": 0.15,
    }
    return mock
