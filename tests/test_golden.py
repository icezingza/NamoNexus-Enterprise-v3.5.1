from math import sqrt

import pytest

from core_engine import calculate_harmonic_risk
from utils import fibonacci_retry


def test_calculate_harmonic_risk_weighting():
    phi = (1 + sqrt(5)) / 2
    expected = (0.8 * phi + 0.2) / (phi + 1)
    assert calculate_harmonic_risk(0.8, 0.2) == pytest.approx(expected)


def test_calculate_harmonic_risk_clamps():
    assert calculate_harmonic_risk(2.0, 2.0) == 1.0
    assert calculate_harmonic_risk(-1.0, -1.0) == 0.0


def test_fibonacci_retry_sequence():
    assert fibonacci_retry(1, base_seconds=0.5) == 0.5
    assert fibonacci_retry(2, base_seconds=0.5) == 0.5
    assert fibonacci_retry(3, base_seconds=0.5) == 1.0
    assert fibonacci_retry(10, base_seconds=1.0, max_seconds=5.0) == 5.0
