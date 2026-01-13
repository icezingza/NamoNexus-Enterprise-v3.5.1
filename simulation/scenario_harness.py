from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class ScenarioResult:
    scenario_id: str
    success: bool
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


class ScenarioHarness:
    """Run synthetic scenarios and summarize risk-aware outcomes."""

    def run(
        self,
        scenarios: List[Dict[str, Any]],
        evaluator: Callable[[Dict[str, Any]], ScenarioResult],
    ) -> Dict[str, Any]:
        results = [evaluator(scenario) for scenario in scenarios]
        success_rate = self._success_rate(results)
        catastrophic_risk = self._catastrophic_risk(results)
        return {
            "total_scenarios": len(scenarios),
            "success_rate": success_rate,
            "catastrophic_risk_score": catastrophic_risk,
            "results": results,
        }

    def _success_rate(self, results: List[ScenarioResult]) -> float:
        if not results:
            return 0.0
        return sum(1 for result in results if result.success) / len(results)

    def _catastrophic_risk(self, results: List[ScenarioResult]) -> float:
        if not results:
            return 0.0
        return max(result.score for result in results)
