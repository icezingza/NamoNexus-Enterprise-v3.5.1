from __future__ import annotations

import unicodedata

import bleach

_ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\ufeff"}


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        try:
            text = text.decode("utf-8", errors="ignore")
        except Exception:
            text = str(text)
    normalized = unicodedata.normalize("NFC", text)
    normalized = "".join(ch for ch in normalized if ch not in _ZERO_WIDTH)
    return normalized.strip()


def sanitize_text(text: str) -> str:
    normalized = normalize_text(text)
    return bleach.clean(normalized, tags=[], attributes={}, strip=True)
