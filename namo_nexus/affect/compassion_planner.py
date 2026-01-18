from typing import Dict, Any, Optional

from src.i18n import load_locale


_LOCALE = load_locale("th")


class CompassionPlanner:
    """Plans a compassionate, grounded reply."""

    def plan_reply(
        self,
        original_message: str,
        dharma_view: Dict[str, Any],
        emotion: Dict[str, Any],
        safe_template: Optional[str],
    ) -> str:
        if safe_template:
            return safe_template

        locale_compassion = _LOCALE["namo_nexus"]["compassion_planner"]
        base = locale_compassion["base"]
        if emotion["distress_level"] == "high":
            base = f"{base} {locale_compassion['high_distress']}"
        base = f"{base} {locale_compassion['closing']}"

        return base
