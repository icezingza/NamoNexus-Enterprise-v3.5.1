from dataclasses import asdict, dataclass
from typing import Dict, List
import time


@dataclass
class Memory:
    id: str
    user_id: str
    event: str
    emotion: str
    emotion_intensity: float
    alignment_insight: str
    timestamp: float
    importance: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class MemoryService:
    def __init__(self) -> None:
        self.memory_store: Dict[str, List[Memory]] = {}

    def store_experience(
        self,
        user_id: str,
        event: str,
        emotion: str,
        emotion_intensity: float,
        alignment_insight: str = "",
    ) -> Dict[str, object]:
        memory_id = f"{user_id}_{int(time.time() * 1000)}"
        memory = Memory(
            id=memory_id,
            user_id=user_id,
            event=event,
            emotion=emotion,
            emotion_intensity=emotion_intensity,
            alignment_insight=alignment_insight,
            timestamp=time.time(),
            importance=min(1.0, max(0.1, emotion_intensity / 10.0)),
        )

        self.memory_store.setdefault(user_id, []).append(memory)
        return memory.to_dict()

    def retrieve_user_context(self, user_id: str, days_back: int = 30) -> List[Dict[str, object]]:
        if user_id not in self.memory_store:
            return []

        cutoff_time = time.time() - (days_back * 24 * 3600)
        relevant = [m for m in self.memory_store[user_id] if m.timestamp >= cutoff_time]
        relevant.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        return [m.to_dict() for m in relevant]

    def analyze_memory_pattern(self, user_id: str) -> Dict[str, object]:
        memories = self.memory_store.get(user_id, [])
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


memory_service = MemoryService()
