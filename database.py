from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from cache import CacheBackend, DEFAULT_CACHE_TTL, InMemoryCache

try:
    from pysqlcipher3 import dbapi2 as sqlcipher
except ImportError:  # pragma: no cover - optional dependency
    try:
        import sqlcipher3 as sqlcipher
    except ImportError:  # pragma: no cover - optional dependency
        sqlcipher = None


class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool with WAL mode enabled."""

    def __init__(
        self, db_path: str, pool_size: int = 5, cipher_key: Optional[str] = None
    ) -> None:
        self.db_path = db_path
        self.pool_size = pool_size
        self.cipher_key = cipher_key or os.getenv("DB_CIPHER_KEY")
        self._local = threading.local()
        self._semaphore = threading.BoundedSemaphore(pool_size)
        self._schema_lock = threading.Lock()
        self._init_schema()

    def _connect(self, timeout: float = 10.0) -> sqlite3.Connection:
        if self.cipher_key:
            if sqlcipher is None:
                raise RuntimeError("DB_CIPHER_KEY set but pysqlcipher3 is not installed")
            conn = sqlcipher.connect(
                self.db_path,
                check_same_thread=False,
                timeout=timeout,
            )
            cursor = conn.cursor()
            safe_key = self.cipher_key.replace("'", "''")
            cursor.execute(f"PRAGMA key = '{safe_key}'")
            cursor.execute("PRAGMA cipher = 'aes-256-cfb'")
            cursor.close()
        else:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=timeout,
            )
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _init_schema(self) -> None:
        """Create schema once at startup."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        with self._schema_lock:
            conn = self._connect()

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    message TEXT,
                    response TEXT,
                    risk_level TEXT,
                    dharma_score REAL,
                    multimodal_data TEXT,
                    timestamp TEXT,
                    node_id TEXT DEFAULT 'TH-GRID-01'
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS crisis_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    risk_level TEXT,
                    alert_type TEXT,
                    empathy_prompts TEXT,
                    timestamp TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
                """
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_user ON conversations(user_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_alerts_session ON crisis_alerts(session_id)"
            )
            conn.commit()
            conn.close()

    def _get_or_create_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            self._local.conn = self._connect()
        return self._local.conn

    @contextmanager
    def get_connection(self):
        """Yield a pooled connection and auto-commit/rollback."""
        self._semaphore.acquire()
        conn = self._get_or_create_conn()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            self._semaphore.release()

    def ping(self) -> None:
        with self.get_connection() as conn:
            conn.execute("SELECT 1")


class GridIntelligence:
    """Sovereign storage layer using SQLite with a connection pool."""

    def __init__(
        self,
        db_path: str,
        cache: Optional[CacheBackend] = None,
        cipher_key: Optional[str] = None,
    ) -> None:
        self.db_pool = DatabaseConnectionPool(
            db_path, pool_size=10, cipher_key=cipher_key
        )
        self.cache = cache or InMemoryCache()

    def store_sovereign(self, data: Dict) -> None:
        """Store conversation data; embeddings (paraphrase-multilingual-MiniLM-L12-v2) can be added later."""
        with self.db_pool.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversations
                (user_id, session_id, message, response, risk_level,
                 dharma_score, multimodal_data, timestamp, node_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["user_id"],
                    data["session_id"],
                    data["message"],
                    data["response"],
                    data["risk_level"],
                    data["dharma_score"],
                    json.dumps(data.get("multimodal", {})),
                    datetime.now().isoformat(),
                    "TH-GRID-01",
                ),
            )

    def create_crisis_alert(self, data: Dict) -> List[str]:
        empathy_prompts = self._generate_empathy_prompts(data["risk_level"])
        with self.db_pool.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO crisis_alerts
                (user_id, session_id, risk_level, alert_type, empathy_prompts, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    data["user_id"],
                    data["session_id"],
                    data["risk_level"],
                    "immediate_intervention",
                    json.dumps(empathy_prompts),
                    datetime.now().isoformat(),
                ),
            )
        self._invalidate_session_cache(data["session_id"])
        self._invalidate_global_cache()
        return empathy_prompts

    async def create_crisis_alert_async(self, data: Dict) -> List[str]:
        return await asyncio.to_thread(self.create_crisis_alert, data)

    def _generate_empathy_prompts(self, risk_level: str) -> List[str]:
        prompts = {
            "severe": [
                "ผู้ใช้อยู่ในภาวะวิกฤตสูง - ใช้น้ำเสียงอ่อนโยนและแสดงความเห็นใจ",
                "ฟังอย่างตั้งใจ อย่าตัดสิน ยืนยันความรู้สึกของเขา",
                "ถามเกี่ยวกับแผนการทำร้ายตัวเอง (means, intent, plan)",
                "อยู่กับเขาจนกว่าจะปลอดภัย - อย่าปล่อยให้อยู่คนเดียว",
            ],
            "moderate": [
                "แสดงความเข้าใจและเห็นใจ",
                "สำรวจแหล่งสนับสนุนทางสังคม",
                "เสนอทางเลือกและกลยุทธ์การรับมือ",
                "ติดตามผลอย่างสม่ำเสมอ",
            ],
            "low": [
                "สร้างบรรยากาศที่อบอุ่น",
                "ส่งเสริมการดูแลตนเอง",
                "ชื่นชมความกล้าที่ขอความช่วยเหลือ",
            ],
        }
        return prompts.get(risk_level, prompts["low"])

    def get_session_history(self, session_id: str) -> List[Dict]:
        cache_key = self._cache_key("session_history", session_id)
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        with self.db_pool.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT message, response, risk_level, dharma_score, timestamp
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                """,
                (session_id,),
            )
            result = [
                {
                    "message": row[0],
                    "response": row[1],
                    "risk": row[2],
                    "dharma": row[3],
                    "time": row[4],
                }
                for row in cursor.fetchall()
            ]

    def get_alerts(self, session_id: str) -> List[Dict]:
        cache_key = self._cache_key("session_alerts", session_id)
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        with self.db_pool.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT risk_level, empathy_prompts, timestamp, resolved
                FROM crisis_alerts
                WHERE session_id = ?
                ORDER BY timestamp DESC
                """,
                (session_id,),
            )
            alerts = []
            for row in cursor.fetchall():
                prompts = json.loads(row[1]) if row[1] else []
                alerts.append(
                    {
                        "risk": row[0],
                        "prompts": prompts,
                        "time": row[2],
                        "resolved": bool(row[3]),
                    }
                )
            return alerts

    def get_global_metrics(self) -> List[Dict]:
        """Fetch historical risk levels and dharma scores for graph visualization."""
        cache_key = self._cache_key("global_metrics")
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        with self.db_pool.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, risk_level, dharma_score
                FROM conversations
                ORDER BY timestamp ASC
                LIMIT 100
                """
            )
            result = [
                {"time": row[0], "risk": row[1], "dharma": row[2]}
                for row in cursor.fetchall()
            ]

    def get_recent_sessions(self) -> List[Dict]:
        """Fetch unique recent sessions for the monitor."""
        cache_key = self._cache_key("recent_sessions")
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        with self.db_pool.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT conversations.session_id, conversations.user_id, latest.last_active
                FROM conversations
                JOIN (
                    SELECT session_id, MAX(timestamp) AS last_active
                    FROM conversations
                    GROUP BY session_id
                ) AS latest
                ON conversations.session_id = latest.session_id
                AND conversations.timestamp = latest.last_active
                ORDER BY latest.last_active DESC
                LIMIT 20
                """
            )
            result = [
                {"session_id": row[0], "user_id": row[1], "last_active": row[2]}
                for row in cursor.fetchall()
            ]

    def get_all_alerts(self) -> List[Dict]:
        """Fetch all active crisis alerts."""
        cache_key = self._cache_key("all_alerts")
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        with self.db_pool.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT user_id, session_id, risk_level, timestamp, resolved
                FROM crisis_alerts
                WHERE resolved = 0
                ORDER BY timestamp DESC
                """
            )
            result = [
                {
                    "user_id": row[0],
                    "session_id": row[1],
                    "risk": row[2],
                    "time": row[3],
                    "resolved": bool(row[4]),
                }
                for row in cursor.fetchall()
            ]
