from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


DEFAULT_LOCALE = os.getenv("NAMO_NEXUS_LOCALE", "th")
LOCALES_DIR = Path(__file__).resolve().parent / "locales"


@lru_cache(maxsize=4)
def load_locale(locale: str | None = None) -> Dict[str, Any]:
    name = (locale or DEFAULT_LOCALE).strip().lower()
    path = LOCALES_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Locale file not found: {path}")
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)
