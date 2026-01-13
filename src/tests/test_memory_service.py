from src.services.memory_service import MemoryService


def test_store_and_retrieve_memory(db_session):
    service = MemoryService()
    stored = service.store_experience(
        db_session,
        user_id="user_001",
        event="Felt anxious about work",
        emotion="anxiety",
        emotion_intensity=7.5,
        alignment_insight="Pause and breathe",
    )
    assert stored["user_id"] == "user_001"
    assert stored["emotion"] == "anxiety"

    memories = service.retrieve_user_context(db_session, user_id="user_001", days_back=1)
    assert len(memories) == 1
    assert memories[0]["event"] == "Felt anxious about work"


def test_analyze_memory_pattern(db_session):
    service = MemoryService()
    service.store_experience(
        db_session,
        user_id="user_002",
        event="Felt sad",
        emotion="sadness",
        emotion_intensity=6.0,
        alignment_insight="",
    )
    service.store_experience(
        db_session,
        user_id="user_002",
        event="Felt sad again",
        emotion="sadness",
        emotion_intensity=6.5,
        alignment_insight="",
    )

    summary = service.analyze_memory_pattern(db_session, user_id="user_002")
    assert summary["total"] == 2
    assert summary["dominant_emotion"] == "sadness"
