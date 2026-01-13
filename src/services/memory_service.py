"""Memory service backed by the database."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session

from src.database.repositories import MemoryRepository
from src.utils.exceptions import InvalidInputError, ServiceError
from src.utils.logger import logger


class MemoryService:
    """Persist and retrieve memory records."""

    def store_experience(
        self,
        db: Session,
        user_id: str,
        event: str,
        emotion: str,
        emotion_intensity: float,
        alignment_insight: str = "",
    ) -> Dict[str, object]:
        try:
            if not event or not isinstance(event, str):
                raise InvalidInputError("Event must be a non-empty string")

            importance = min(1.0, max(0.1, emotion_intensity / 10.0))
            repo = MemoryRepository(db)
            memory = repo.create_memory(
                {
                    "user_id": user_id,
                    "event": event,
                    "emotion": emotion,
                    "emotion_intensity": emotion_intensity,
                    "alignment_insight": alignment_insight,
                    "importance": importance,
                }
            )
            logger.info("Memory stored", extra={"user_id": user_id, "memory_id": memory.id})
            return self._to_dict(memory)
        except InvalidInputError:
            raise
        except Exception as exc:  # noqa: BLE001 - wrap unexpected errors
            logger.error("Failed to store memory", exc_info=True)
            raise ServiceError(f"Failed to store memory: {exc}") from exc

    def retrieve_user_context(self, db: Session, user_id: str, days_back: int = 30) -> List[Dict[str, object]]:
        repo = MemoryRepository(db)
        memories = repo.get_user_memories(user_id, days_back=days_back)
        return [self._to_dict(memory) for memory in memories]

    def analyze_memory_pattern(self, db: Session, user_id: str) -> Dict[str, object]:
        repo = MemoryRepository(db)
        memories = repo.get_user_memories(user_id, days_back=3650)
        if not memories:
            return {"total": 0, "dominant_emotion": "neutral", "distribution": {}}

        distribution: Dict[str, int] = {}
        for memory in memories:
            distribution[memory.emotion] = distribution.get(memory.emotion, 0) + 1

        dominant = max(distribution, key=distribution.get)
        return {
            "total": len(memories),
            "dominant_emotion": dominant,
            "distribution": distribution,
        }

    @staticmethod
    def _to_dict(memory: object) -> Dict[str, object]:
        return {
            "id": getattr(memory, "id"),
            "user_id": getattr(memory, "user_id"),
            "event": getattr(memory, "event"),
            "emotion": getattr(memory, "emotion"),
            "emotion_intensity": getattr(memory, "emotion_intensity"),
            "alignment_insight": getattr(memory, "alignment_insight"),
            "importance": getattr(memory, "importance"),
            "created_at": getattr(memory, "created_at", datetime.utcnow()).isoformat(),
        }


memory_service = MemoryService()
