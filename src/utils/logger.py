"""Logging helpers for NamoNexus."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict


def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """Initialize a logger with console and file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"namonexus_{datetime.utcnow().strftime('%Y%m%d')}.log")
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger("namonexus", os.getenv("LOG_LEVEL", "INFO"))


def log_interaction(
    user_id: str,
    message: str,
    response: Dict[str, Any],
    emotion: str,
    risk_score: float,
) -> None:
    """Log a summarized interaction record."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "message": message[:100],
        "emotion": emotion,
        "risk_score": risk_score,
        "response_preview": response.get("response", "")[:100],
    }
    logger.info(json.dumps(log_data))


def log_error(error_type: str, user_id: str, error_message: str, traceback_str: str) -> None:
    """Log a structured error event."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": error_type,
        "user_id": user_id,
        "error_message": error_message,
        "traceback": traceback_str,
    }
    logger.error(json.dumps(log_data))
