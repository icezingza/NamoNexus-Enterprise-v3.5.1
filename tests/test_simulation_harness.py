from simulation.scenario_harness import ScenarioHarness, ScenarioResult


def test_scenario_harness_summary():
    harness = ScenarioHarness()
    scenarios = [
        {"id": "ok"},
        {"id": "fail"},
    ]

    def evaluator(scenario):
        if scenario["id"] == "ok":
            return ScenarioResult(scenario_id="ok", success=True, score=0.1)
        return ScenarioResult(scenario_id="fail", success=False, score=0.9)

    summary = harness.run(scenarios, evaluator)
    assert summary["total_scenarios"] == 2
    assert summary["success_rate"] == 0.5
    assert summary["catastrophic_risk_score"] == 0.9
