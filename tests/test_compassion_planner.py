import pytest

from namo_nexus.affect.compassion_planner import CompassionPlanner
from src.i18n import load_locale


LOCALE = load_locale("th")
COMPASSION = LOCALE["namo_nexus"]["compassion_planner"]

def test_compassion_planner_safe_template():
    planner = CompassionPlanner()
    result = planner.plan_reply(
        original_message="Hello",
        dharma_view={},
        emotion={"distress_level": "low"},
        safe_template="Safe reply"
    )
    assert result == "Safe reply"

def test_compassion_planner_high_distress():
    planner = CompassionPlanner()
    result = planner.plan_reply(
        original_message="I feel bad",
        dharma_view={},
        emotion={"distress_level": "high"},
        safe_template=None
    )
    expected = f"{COMPASSION['base']} {COMPASSION['high_distress']} {COMPASSION['closing']}"
    assert result == expected

def test_compassion_planner_low_distress():
    planner = CompassionPlanner()
    result = planner.plan_reply(
        original_message="I am okay",
        dharma_view={},
        emotion={"distress_level": "low"},
        safe_template=None
    )
    expected = f"{COMPASSION['base']} {COMPASSION['closing']}"
    assert result == expected
