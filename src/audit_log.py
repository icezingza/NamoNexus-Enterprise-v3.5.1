from __future__ import annotations

import datetime
import json

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_log"

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
    ip_addr: str,
    user_agent: str,
    payload: dict,
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
