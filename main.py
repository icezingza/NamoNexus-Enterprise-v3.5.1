from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Dict

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer

from core_engine import HarmonicGovernor
from database import GridIntelligence
from models import MultiModalAnalysis, TriageRequest, TriageResponse

AUTH_TOKEN = os.getenv("NAMO_NEXUS_TOKEN", "namo-nexus-enterprise-2026")
DB_PATH = os.getenv("DB_PATH", os.path.join("data", "namo_nexus_sovereign.db"))

app = FastAPI(
    title="NamoNexus Enterprise API",
    version="3.5.1",
    description="Mental Health Infrastructure AI - Production Hardened",
)
security = HTTPBearer()


class NamoNexusEnterprise:
    """Main triage engine for NamoNexus Enterprise v3.5.1."""

    def __init__(self, db_path: str) -> None:
        self.governor = HarmonicGovernor()
        self.grid = GridIntelligence(db_path)

    async def process_triage(
        self, request: TriageRequest, background_tasks: BackgroundTasks
    ) -> TriageResponse:
        start = time.time()
        session_id = request.session_id or self._generate_session_id()

        result = await self.governor.orchestrate(
            request.message,
            request.voice_features,
            request.facial_features,
        )

        multimodal = result["multimodal"]
        ethics = result["ethics"]
        response_text = self._generate_response(request.message, ethics, multimodal)
        human_required = ethics["requires_human"] and multimodal.combined_risk > 0.7

        background_tasks.add_task(
            self._background_process,
            request,
            session_id,
            response_text,
            ethics,
            multimodal,
            human_required,
        )

        latency = (time.time() - start) * 1000

        return TriageResponse(
            response=response_text,
            risk_level=ethics["risk_level"],
            dharma_score=ethics["dharma_score"],
            emotional_tone=ethics["emotional_tone"],
            multimodal_confidence=multimodal.confidence,
            latency_ms=latency,
            session_id=session_id,
            human_handoff_required=human_required,
            empathy_prompts=(
                self.grid._generate_empathy_prompts(ethics["risk_level"])
                if human_required
                else None
            ),
        )

    def _generate_response(
        self, message: str, ethics: Dict, multimodal: MultiModalAnalysis
    ) -> str:
        tone = ethics["emotional_tone"]
        risk = ethics["risk_level"]

        if tone == "compassionate":
            greeting = "พี่ครับ ผมรู้สึกว่าพี่กำลังลำบากใจมากนะ "
        elif tone == "supportive":
            greeting = "สวัสดีครับ ผมพร้อมรับฟังพี่นะ "
        else:
            greeting = "สวัสดีครับ "

        if risk == "severe":
            main = "ผมเห็นว่าพี่กำลังเจอช่วงเวลาที่ยากลำบากมาก พี่ไม่ได้อยู่คนเดียวนะครับ ให้ผมช่วยพี่ได้ไหม"
        elif risk == "moderate":
            main = "ขอบคุณที่ไว้วางใจเล่าให้ฟังนะครับ ผมเข้าใจความรู้สึกของพี่"
        else:
            main = "ยินดีที่ได้พูดคุยกับพี่ครับ"

        dharma_note = ""
        if ethics["principles"]:
            dharma_note = f" (หลักธรรม: {', '.join(ethics['principles'])})"

        return f"{greeting}{main}{dharma_note}"

    def _background_process(
        self,
        request: TriageRequest,
        session_id: str,
        response: str,
        ethics: Dict,
        multimodal: MultiModalAnalysis,
        human_required: bool,
    ) -> None:
        self.grid.store_sovereign(
            {
                "user_id": request.user_id,
                "session_id": session_id,
                "message": request.message,
                "response": response,
                "risk_level": ethics["risk_level"],
                "dharma_score": ethics["dharma_score"],
                "multimodal": {
                    "combined_risk": multimodal.combined_risk,
                    "confidence": multimodal.confidence,
                },
            }
        )

        if human_required:
            self.grid.create_crisis_alert(
                {
                    "user_id": request.user_id,
                    "session_id": session_id,
                    "risk_level": ethics["risk_level"],
                }
            )
            print(
                f"▲ CRISIS ALERT: User {request.user_id} requires immediate human intervention"
            )

    @staticmethod
    def _generate_session_id() -> str:
        return f"session_{int(time.time())}"


engine = NamoNexusEnterprise(DB_PATH)


@app.post("/triage", response_model=TriageResponse)
async def triage_endpoint(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    credentials=Depends(security),
):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await engine.process_triage(request, background_tasks)


@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "system": "NamoNexus Enterprise",
        "version": "3.5.1",
        "grid_status": "sovereign",
        "fixes": ["connection_pool", "non_blocking_io"],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/harmonic-console")
async def get_harmonic_console_global(credentials=Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401)

    metrics = engine.grid.get_global_metrics()
    sessions = engine.grid.get_recent_sessions()
    alerts = engine.grid.get_all_alerts()

    return {
        "metrics": metrics,
        "recent_sessions": sessions,
        "active_alerts": alerts,
    }


@app.get("/harmonic-console/{session_id}")
async def get_harmonic_console_session(session_id: str, credentials=Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401)

    history = engine.grid.get_session_history(session_id)
    alerts = engine.grid.get_alerts(session_id)

    return {
        "session_id": session_id,
        "conversation_history": history,
        "crisis_alerts": alerts,
        "empathy_guidance": alerts[0]["prompts"] if alerts else [],
    }
