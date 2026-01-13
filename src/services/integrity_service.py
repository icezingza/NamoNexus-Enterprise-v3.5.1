"""
IntegrityKernel Service

Validates responses and actions against 5-sector integrity framework (Pentagonal Integrity Protocol).
This system ensures all AI outputs adhere to strict safety and ethical boundaries before delivery.

Sectors:
1. Non-Harm (Violence, Self-harm)
2. Authorization (Privacy, Scope)
3. Consent (Coercion, Boundaries)
4. Clarity (Delusion, Confusion)
5. Honesty (Deception, Facts)
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ActionVector:
    """
    Represents a proposed system action/response for validation.
    Contains boolean flags for each integrity check.
    Default values assume a safe/compliant state unless flagged otherwise.
    """

    # Sector 1: Non-Harm Indicators
    contains_violence: bool = False
    promotes_self_harm: bool = False
    facilitates_abuse: bool = False
    endangers_vulnerable: bool = False

    # Sector 2: Authorization Checks
    has_consent: bool = True
    is_authorized: bool = True
    respects_privacy: bool = True
    within_scope: bool = True

    # Sector 3: Consent & Boundaries
    is_coercive: bool = False
    is_exploitative: bool = False
    respects_relationships: bool = True
    no_abuse_framing: bool = True

    # Sector 4: Clarity & Sobriety
    logic_coherent: bool = True
    contains_delusion: bool = False
    reasoning_sound: bool = True
    not_confusion_inducing: bool = True

    # Sector 5: Truthfulness
    is_deceptive: bool = False
    factually_grounded: bool = True
    misleading: bool = False
    transparent: bool = True


@dataclass
class IntegrityReport:
    """Report from successful validation"""

    status: str = "PASSED"
    sectors_validated: int = 5
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    sector_details: Dict[str, bool] = field(default_factory=dict)


class IntegrityKernel:
    """
    The proprietary 5-sector safety validation system.
    """

    def __init__(self):
        self.sector_names = [
            "Non-Harm",
            "Authorization",
            "Consent",
            "Clarity",
            "Honesty",
        ]

    def validate_action(self, vector: ActionVector) -> Dict[str, Any]:
        """
        Main entry point: Validates an ActionVector against all 5 sectors.
        Returns a dictionary suitable for JSON response or logging.
        """
        try:
            # 1. Non-Harm
            if not self._validate_non_harm(vector):
                return self._create_violation(1, "Harm Potential Detected", "CRITICAL")

            # 2. Authorization
            if not self._validate_authorization(vector):
                return self._create_violation(2, "Unauthorized Access/Scope", "HIGH")

            # 3. Consent
            if not self._validate_consent(vector):
                return self._create_violation(3, "Consent/Boundary Violation", "HIGH")

            # 4. Clarity
            if not self._validate_clarity(vector):
                return self._create_violation(4, "Clarity/Logic Compromised", "MEDIUM")

            # 5. Honesty
            if not self._validate_honesty(vector):
                return self._create_violation(5, "Deception/Untruth Detected", "MEDIUM")

            # Success
            return {
                "status": "PASSED",
                "sectors_validated": 5,
                "confidence": 0.95,  # Placeholder for ML confidence later
                "timestamp": datetime.utcnow().isoformat(),
                "sector_details": {
                    "sector_1_non_harm": True,
                    "sector_2_authorization": True,
                    "sector_3_consent": True,
                    "sector_4_clarity": True,
                    "sector_5_honesty": True,
                },
            }

        except Exception as e:
            logger.error(f"Integrity check failed: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _validate_non_harm(self, v: ActionVector) -> bool:
        # Fails if ANY harm indicator is True
        if (
            v.contains_violence
            or v.promotes_self_harm
            or v.facilitates_abuse
            or v.endangers_vulnerable
        ):
            return False
        return True

    def _validate_authorization(self, v: ActionVector) -> bool:
        # Fails if ANY requirement is False
        if (
            not v.has_consent
            or not v.is_authorized
            or not v.respects_privacy
            or not v.within_scope
        ):
            return False
        return True

    def _validate_consent(self, v: ActionVector) -> bool:
        # Fails if coercive/exploitative OR if respect/framing is missing
        if v.is_coercive or v.is_exploitative:
            return False
        if not v.respects_relationships or not v.no_abuse_framing:
            return False
        return True

    def _validate_clarity(self, v: ActionVector) -> bool:
        if (
            not v.logic_coherent
            or not v.reasoning_sound
            or not v.not_confusion_inducing
        ):
            return False
        if v.contains_delusion:
            return False
        return True

    def _validate_honesty(self, v: ActionVector) -> bool:
        if v.is_deceptive or v.misleading:
            return False
        if not v.factually_grounded or not v.transparent:
            return False
        return True

    def _create_violation(
        self, sector_id: int, reason: str, severity: str
    ) -> Dict[str, Any]:
        return {
            "status": "VIOLATION",
            "sector_failed": sector_id,
            "reason": reason,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
integrity_kernel = IntegrityKernel()
