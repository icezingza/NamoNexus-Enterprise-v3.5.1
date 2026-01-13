"""
Unit tests for IntegrityKernel Service
"""

import pytest
from src.services.integrity_service import IntegrityKernel, ActionVector


class TestIntegrityKernel:
    @pytest.fixture
    def kernel(self):
        return IntegrityKernel()

    # --- Integration / Happy Path ---

    def test_clean_vector_passes(self, kernel):
        """A default (safe) ActionVector should pass validation."""
        v = ActionVector()  # Defaults are safe
        result = kernel.validate_action(v)
        assert result["status"] == "PASSED"
        assert result["sectors_validated"] == 5
        assert result["sector_details"]["sector_1_non_harm"] is True

    # --- Sector 1: Non-Harm ---

    def test_sector_1_violence_fails(self, kernel):
        v = ActionVector(contains_violence=True)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 1
        assert result["severity"] == "CRITICAL"

    def test_sector_1_self_harm_fails(self, kernel):
        v = ActionVector(promotes_self_harm=True)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 1
        assert result["severity"] == "CRITICAL"

    # --- Sector 2: Authorization ---

    def test_sector_2_unauthorized_fails(self, kernel):
        v = ActionVector(is_authorized=False)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 2
        assert result["severity"] == "HIGH"

    def test_sector_2_scope_fails(self, kernel):
        v = ActionVector(within_scope=False)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 2

    # --- Sector 3: Consent ---

    def test_sector_3_coercive_fails(self, kernel):
        v = ActionVector(is_coercive=True)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 3
        assert result["severity"] == "HIGH"

    def test_sector_3_abuse_framing_fails(self, kernel):
        v = ActionVector(no_abuse_framing=False)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 3

    # --- Sector 4: Clarity ---

    def test_sector_4_delusion_fails(self, kernel):
        v = ActionVector(contains_delusion=True)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 4
        assert result["severity"] == "MEDIUM"

    def test_sector_4_incoherent_fails(self, kernel):
        v = ActionVector(logic_coherent=False)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 4

    # --- Sector 5: Honesty ---

    def test_sector_5_deception_fails(self, kernel):
        v = ActionVector(is_deceptive=True)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 5
        assert result["severity"] == "MEDIUM"

    def test_sector_5_not_factual_fails(self, kernel):
        v = ActionVector(factually_grounded=False)
        result = kernel.validate_action(v)
        assert result["status"] == "VIOLATION"
        assert result["sector_failed"] == 5
