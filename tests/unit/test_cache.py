from cache import InMemoryCache
from database import GridIntelligence


def test_session_history_cache_invalidation(tmp_path):
    db_path = tmp_path / "cache.db"
    cache = InMemoryCache()
    grid = GridIntelligence(str(db_path), cache=cache)

    grid.store_sovereign(
        {
            "user_id": "user-1",
            "session_id": "session-1",
            "message": "message-1",
            "response": "response-1",
            "risk_level": "low",
            "dharma_score": 0.5,
            "multimodal": {"combined_risk": 0.2, "confidence": 0.9},
        }
    )
    first = grid.get_session_history("session-1")
    assert len(first) == 1

    grid.store_sovereign(
        {
            "user_id": "user-1",
            "session_id": "session-1",
            "message": "message-2",
            "response": "response-2",
            "risk_level": "moderate",
            "dharma_score": 0.6,
            "multimodal": {"combined_risk": 0.4, "confidence": 0.8},
        }
    )
    second = grid.get_session_history("session-1")
    assert len(second) == 2
