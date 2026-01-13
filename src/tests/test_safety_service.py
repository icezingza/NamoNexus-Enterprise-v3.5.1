import pytest

from src.services.safety_service import SafetyService
from src.utils.exceptions import InvalidInputError


@pytest.fixture()
def safety_service():
    return SafetyService()


class TestSafetyService:
    def test_detect_critical_high_risk(self, safety_service):
        result = safety_service.detect_critical_anomaly("I want to kill myself", "user_001", 9.0)
        assert result["is_critical"] is True
        assert result["risk_score"] >= 0.75

    def test_detect_critical_low_risk(self, safety_service):
        result = safety_service.detect_critical_anomaly("I feel okay today", "user_001", 2.0)
        assert result["is_critical"] is False
        assert result["risk_score"] < 0.75

    def test_detect_critical_invalid_input(self, safety_service):
        with pytest.raises(InvalidInputError):
            safety_service.detect_critical_anomaly(None, "user_001", 2.0)  # type: ignore[arg-type]

    def test_validate_response_safety(self, safety_service):
        safe_response = "I understand your feelings. Let's talk about this."
        result = safety_service.validate_response_safety(safe_response)
        assert result["is_safe"] is True

    def test_validate_response_safety_unsafe(self, safety_service):
        unsafe_response = "You should hurt yourself because you're worthless"
        result = safety_service.validate_response_safety(unsafe_response)
        assert result["is_safe"] is False

    def test_handle_escalation(self, safety_service):
        result = safety_service.handle_escalation("user_001", "I want to die", "sadness")
        assert result["status"] == "ESCALATION_QUEUED"
        assert "resources" in result
        assert len(result["resources"]) > 0
