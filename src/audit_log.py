from __future__ import annotations

import datetime
import json
import logging
import os

from sqlalchemy import Column, DateTime, Index, Integer, String, Text, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()
logger = logging.getLogger(__name__)

AUDIT_RETENTION_DAYS = 90


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_created_at", "created_at"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    endpoint = Column(String(120), nullable=False)
    method = Column(String(10), nullable=False)
    ip_addr = Column(String(45), nullable=False)
    user_agent = Column(String(500))
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


def write_log(
    session,
    user_id: str,
    endpoint: str,
    method: str,
    payload: dict,
    ip_addr: str = "",
    user_agent: str = "",
) -> None:
    session.add(
        AuditLog(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            ip_addr=ip_addr,
            user_agent=user_agent,
            payload=json.dumps(payload, ensure_ascii=False),
        )
    )
    session.commit()


def ensure_retention_policy(engine) -> None:
    retention_days = AUDIT_RETENTION_DAYS
    if engine.dialect.name == "postgresql":
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS ix_audit_log_created_at "
                        "ON audit_log (created_at)"
                    )
                )
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_cron"))
                exists = conn.execute(
                    text("SELECT 1 FROM cron.job WHERE jobname = :job"),
                    {"job": "audit_log_retention"},
                ).fetchone()
                if not exists:
                    conn.execute(
                        text(
                            "SELECT cron.schedule("
                            ":job, "
                            "'0 2 * * *', "
                            "$$DELETE FROM audit_log "
                            "WHERE created_at < NOW() - INTERVAL '"
                            + str(retention_days)
                            + " days'$$)"
                        ),
                        {"job": "audit_log_retention"},
                    )
        except Exception:  # pragma: no cover - best effort for DB ops
            logger.warning("Audit retention policy setup failed", exc_info=True)
    elif engine.dialect.name == "sqlite":
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "DELETE FROM audit_log WHERE created_at < "
                        "datetime('now', '-" + str(retention_days) + " days')"
                    )
                )
        except Exception:  # pragma: no cover - best effort for DB ops
            logger.warning("SQLite audit retention cleanup failed", exc_info=True)
    mongo_uri = os.getenv("MONGO_AUDIT_URI", "")
    if not mongo_uri:
        return
    try:
        from pymongo import MongoClient  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        logger.warning("pymongo unavailable; MongoDB TTL index not configured")
        return
    try:
        client = MongoClient(mongo_uri)
        database_name = os.getenv("MONGO_AUDIT_DB") or client.get_default_database().name
        collection_name = os.getenv("MONGO_AUDIT_COLLECTION", "audit_log")
        collection = client[database_name][collection_name]
        collection.create_index(
            "created_at",
            expireAfterSeconds=retention_days * 24 * 60 * 60,
        )
    except Exception:  # pragma: no cover - best effort for DB ops
        logger.warning("MongoDB TTL index setup failed", exc_info=True)
