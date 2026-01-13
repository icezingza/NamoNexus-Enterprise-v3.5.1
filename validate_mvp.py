"""Run a lightweight MVP validation check."""
from __future__ import annotations

import asyncio
import os
from typing import Any

from app.mvp.orchestrator import NamoMvpOrchestrator
from app.mvp.validation_module import ValidationModule


def print_section(title: str) -> None:
    line = "=" * len(title)
    print(line)
    print(title)
    print(line)


def print_kv(data: dict[str, Any]) -> None:
    for key, value in data.items():
        print(f"- {key}: {value}")


async def run_validation() -> None:
    os.environ.setdefault("NAMO_EMOTION_SIM_MODE", "1")
    os.environ.setdefault("NAMO_MEMORY_SIM_MODE", "1")
    os.environ.setdefault(
        "NAMO_FEATURE_FLAGS",
        '{"ENABLE_SAFETY": true, "ENABLE_MEMORY": true, '
        '"ENABLE_DHAMMA_REFLECTION": true, "ENABLE_COHERENCE_SCORE": true, '
        '"ENABLE_LOGGING": true, "ENABLE_INFINITY_MEMORY": false}',
    )

    validator = ValidationModule()
    report = validator.run()

    print_section("Validation Report")
    print(f"status: {report.status}")
    print_kv(report.checks)
    if report.warnings:
        print("warnings:")
        for warning in report.warnings:
            print(f"- {warning}")

    orchestrator = NamoMvpOrchestrator()
    result = await orchestrator.process("I feel anxious today.", "validation")

    print_section("Sample Orchestration")
    print_kv(
        {
            "tone": result.get("tone"),
            "ethical_score": result.get("ethical_score"),
            "decision_consistency": result.get("decision_consistency"),
        }
    )
    if result.get("status") == "blocked":
        print(f"blocked_reason: {result.get('reason')}")


if __name__ == "__main__":
    asyncio.run(run_validation())
