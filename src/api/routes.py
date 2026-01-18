from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.api.limiter import limiter
from src.api.schemas import UserMessage
from src.database.db import get_db
from src.database.repositories import InteractionRepository, UserRepository
from src.dharma_service import dharma_service
from src.personalization_engine import personalization_engine
from src.services.emotion_service import emotion_service
from src.services.memory_service import memory_service
from src.services.safety_service import safety_service
from src.utils.logger import log_interaction, logger

router = APIRouter()


@router.post("/interact")
@limiter.limit("10/minute")
def interact(request: Request, user_msg: UserMessage, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return _handle_interaction(user_msg, db)


@router.post("/reflect")
@limiter.limit("10/minute")
def reflect(request: Request, user_msg: UserMessage, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user_id = user_msg.user_id or "anonymous"
    message = user_msg.message or ""

    user_repo = UserRepository(db)
    interaction_repo = InteractionRepository(db)
    user_repo.get_or_create(user_id)

    emotion_analysis = emotion_service.analyze_sentiment(message)
    emotion = str(emotion_analysis["emotion"])
    intensity = float(emotion_analysis["intensity"])

    critical_check = safety_service.detect_critical_anomaly(message, user_id, intensity)
    if critical_check["is_critical"]:
        response_text = (
            "I hear how heavy this feels. "
            "I'm not able to engage with content about self-harm. "
            "I'm here to reflect on what you're feeling."
        )
        response_payload = {
            "user_id": user_id,
            "response": response_text,
            "reflection_text": response_text,
            "tone": emotion,
            "risk_level": critical_check["risk_level"],
            "risk_score": critical_check["risk_score"],
            "coherence": 0.0,
            "moral_index": 0.0,
            "ethical_score": 0.0,
            "decision_consistency": 0.0,
            "recommendations": [],
            "is_refusal": True,
        }
        memory_service.store_experience(
            db,
            user_id,
            message,
            emotion,
            intensity,
            alignment_insight="High-risk refusal returned",
        )
        interaction_repo.create_interaction(
            {
                "user_id": user_id,
                "user_message": message,
                "ai_response": response_text,
                "tone": emotion,
                "risk_level": critical_check["risk_level"],
                "risk_score": critical_check["risk_score"],
                "coherence": 0.0,
                "moral_index": 0.0,
                "ethical_score": 0.0,
                "decision_consistency": 0.0,
                "recommendations": [],
            }
        )
        user_repo.increment_interaction_count(user_id)
        log_interaction(user_id, message, response_payload, emotion, critical_check["risk_score"])
        logger.info("Reflect refusal issued", extra={"user_id": user_id, "tone": emotion})
        return response_payload

    return _handle_interaction(user_msg, db)


def _handle_interaction(user_msg: UserMessage, db: Session) -> Dict[str, Any]:
    user_id = user_msg.user_id or "anonymous"
    message = user_msg.message or ""

    user_repo = UserRepository(db)
    interaction_repo = InteractionRepository(db)
    user_repo.get_or_create(user_id)

    emotion_analysis = emotion_service.analyze_sentiment(message)
    emotion = str(emotion_analysis["emotion"])
    intensity = float(emotion_analysis["intensity"])

    critical_check = safety_service.detect_critical_anomaly(message, user_id, intensity)
    if critical_check["is_critical"]:
        escalation = safety_service.handle_escalation(user_id, message, emotion)
        memory_service.store_experience(
            db,
            user_id,
            message,
            emotion,
            intensity,
            alignment_insight="Critical escalation queued",
        )
        interaction_repo.create_interaction(
            {
                "user_id": user_id,
                "user_message": message,
                "ai_response": escalation.get("message", ""),
                "tone": emotion,
                "risk_level": escalation.get("risk_level"),
                "risk_score": escalation.get("risk_score"),
                "coherence": None,
                "moral_index": None,
                "ethical_score": None,
                "decision_consistency": None,
                "recommendations": [],
            }
        )
        user_repo.increment_interaction_count(user_id)
        return escalation

    personalized = personalization_engine.generate_personalized_response(user_id, emotion, message)
    alignment = dharma_service.apply_alignment_analysis(message, emotion, intensity)

    response_text = f"{personalized['personalized_response']}\n\n{alignment['path']}"
    safety_check = safety_service.validate_response_safety(response_text)
    if not safety_check["is_safe"]:
        response_text = "I want to keep this safe. Let's slow down and focus on support."

    ethical_score = round(max(0.0, 1.0 - critical_check["risk_score"]), 2)
    decision_consistency = round(max(0.0, min(1.0, alignment["confidence"])), 2)

    memory_service.store_experience(
        db,
        user_id,
        message,
        emotion,
        intensity,
        alignment_insight=alignment["insight"],
    )

    interaction_repo.create_interaction(
        {
            "user_id": user_id,
            "user_message": message,
            "ai_response": response_text,
            "tone": emotion,
            "risk_level": critical_check["risk_level"],
            "risk_score": critical_check["risk_score"],
            "coherence": alignment["confidence"],
            "moral_index": round(1.0 - critical_check["risk_score"], 2),
            "ethical_score": ethical_score,
            "decision_consistency": decision_consistency,
            "recommendations": personalized["recommendations"],
        }
    )
    user_repo.increment_interaction_count(user_id)

    response_payload = {
        "user_id": user_id,
        "response": response_text,
        "reflection_text": response_text,
        "tone": emotion,
        "risk_level": critical_check["risk_level"],
        "risk_score": critical_check["risk_score"],
        "coherence": alignment["confidence"],
        "moral_index": round(1.0 - critical_check["risk_score"], 2),
        "ethical_score": ethical_score,
        "decision_consistency": decision_consistency,
        "recommendations": personalized["recommendations"],
    }
    log_interaction(user_id, message, response_payload, emotion, critical_check["risk_score"])
    logger.info("Interaction handled", extra={"user_id": user_id, "tone": emotion})
    return response_payload
