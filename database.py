from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cache import CacheBackend, DEFAULT_CACHE_TTL, InMemoryCache
from src.i18n import load_locale

try:
    from pysqlcipher3 import dbapi2 as sqlcipher
except ImportError:  # pragma: no cover - optional dependency
    try:
        import sqlcipher3 as sqlcipher
    except ImportError:  # pragma: no cover - optional dependency
        sqlcipher = None


FIBONACCI_DELAYS = [1, 1, 2, 3, 5, 8, 13, 21]
DEFAULT_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_TIMEOUT_SECONDS = float(os.getenv("DB_TIMEOUT_SECONDS", "30"))
DB_BUSY_TIMEOUT_MS = int(DB_TIMEOUT_SECONDS * 1000)
SEMAPHORE_TIMEOUT_SECONDS = float(os.getenv("DB_SEMAPHORE_TIMEOUT", "30"))
_LOCALE = load_locale("th")


def _is_write_query(query: str) -> bool:
    query = query.strip().upper()
    return query.startswith(
        (
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "REPLACE",
            "ALTER",
            "DROP",
        )
    )


class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool with WAL mode and monitoring."""

    def __init__(
        self,
        db_path: str,
        pool_size: int = DEFAULT_POOL_SIZE,
        cipher_key: Optional[str] = None,
    ) -> None:
        self.db_path = db_path
        self.pool_size = pool_size
        self.cipher_key = cipher_key or os.getenv("DB_CIPHER_KEY")
        self.logger = logging.getLogger("namo_nexus.database")
        self._local = threading.local()
        self._semaphore = threading.BoundedSemaphore(pool_size)
        self._schema_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        self._closed = False
        self._stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_retries": 0,
            "lock_waits": 0,
            "connection_count": 0,
        }
        self._init_schema()

    def _connect(self, timeout: float = DB_TIMEOUT_SECONDS) -> sqlite3.Connection:
        if self.cipher_key:
            if "'" in self.cipher_key:
                raise ValueError("Cipher key cannot contain single quotes")
            if sqlcipher is None:
                raise RuntimeError("DB_CIPHER_KEY set but pysqlcipher3 is not installed")
            conn = sqlcipher.connect(
                self.db_path,
                check_same_thread=False,
                timeout=timeout,
            )
            cursor = conn.cursor()
            # Use parameter binding to prevent SQL injection.
            cursor.execute("PRAGMA key = ?", (self.cipher_key,))
            cursor.execute("PRAGMA cipher = 'aes-256-cfb'")
            cursor.close()
        else:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=timeout,
            )
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(f"PRAGMA busy_timeout={DB_BUSY_TIMEOUT_MS}")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Create schema once at startup."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        with self._schema_lock:
            conn = self._connect()
            try:
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
                self.logger.info(
                    "Database initialized (WAL mode, pool=%s) at %s",
                    self.pool_size,
                    self.db_path,
                )
            finally:
                conn.close()

    def _get_or_create_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            self._local.conn = self._connect()
            with self._stats_lock:
                self._stats["connection_count"] += 1
        return self._local.conn

    @contextmanager
    def _acquire_with_timeout(self, timeout: float = SEMAPHORE_TIMEOUT_SECONDS):
        acquired = self._semaphore.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Could not acquire connection within {timeout}s")
        try:
            yield
        finally:
            self._semaphore.release()

    @contextmanager
    def get_connection(self):
        """Yield a pooled connection and auto-commit/rollback."""
        with self._acquire_with_timeout():
            conn = self._get_or_create_conn()
            try:
                yield conn
            except Exception:
                conn.rollback()
                raise
            else:
                conn.commit()

    def execute(
        self,
        query: str,
        params: Sequence[Any] = (),
        fetch_results: bool = True,
    ) -> Optional[List[sqlite3.Row]]:
        if self._closed:
            raise RuntimeError("Database connection pool is closed")
        last_error: Optional[Exception] = None
        start_time = time.monotonic()
        with self._stats_lock:
            self._stats["total_queries"] += 1

        for attempt, delay in enumerate(FIBONACCI_DELAYS, start=1):
            try:
                with self._acquire_with_timeout():
                    conn = self._get_or_create_conn()
                    cursor = conn.execute(query, params)
                    if _is_write_query(query):
                        conn.commit()
                    results = cursor.fetchall() if fetch_results else None
                    with self._stats_lock:
                        self._stats["successful_queries"] += 1
                        if attempt > 1:
                            self._stats["total_retries"] += attempt - 1
                    if attempt > 1:
                        self.logger.info(
                            "Query succeeded after %s attempts (%.2fs)",
                            attempt,
                            time.monotonic() - start_time,
                        )
                    return results
            except (sqlite3.OperationalError, TimeoutError) as exc:
                last_error = exc
                with self._stats_lock:
                    self._stats["lock_waits"] += 1
                if attempt < len(FIBONACCI_DELAYS):
                    self.logger.warning(
                        "DB busy/locked. Retry %s/%s in %ss",
                        attempt,
                        len(FIBONACCI_DELAYS),
                        delay,
                    )
                    time.sleep(delay)
                else:
                    break
            except Exception as exc:
                with self._stats_lock:
                    self._stats["failed_queries"] += 1
                self.logger.error("Query failed: %s", exc, exc_info=True)
                raise

        with self._stats_lock:
            self._stats["failed_queries"] += 1
        self.logger.error(
            "Query failed after retries (%.2fs): %s",
            time.monotonic() - start_time,
            last_error,
        )
        raise last_error or RuntimeError("Database query failed")

    def execute_many(self, query: str, params_list: List[Tuple[Any, ...]]) -> int:
        if self._closed:
            raise RuntimeError("Database connection pool is closed")
        last_error: Optional[Exception] = None

        for attempt, delay in enumerate(FIBONACCI_DELAYS, start=1):
            try:
                with self._acquire_with_timeout():
                    conn = self._get_or_create_conn()
                    cursor = conn.cursor()
                    cursor.executemany(query, params_list)
                    conn.commit()
                    affected_rows = cursor.rowcount
                    with self._stats_lock:
                        self._stats["successful_queries"] += 1
                        if attempt > 1:
                            self._stats["total_retries"] += attempt - 1
                    if attempt > 1:
                        self.logger.info(
                            "Batch succeeded after %s attempts (%s rows)",
                            attempt,
                            affected_rows,
                        )
                    return affected_rows
            except (sqlite3.OperationalError, TimeoutError) as exc:
                last_error = exc
                with self._stats_lock:
                    self._stats["lock_waits"] += 1
                if attempt < len(FIBONACCI_DELAYS):
                    self.logger.warning(
                        "Batch busy. Retry %s/%s in %ss",
                        attempt,
                        len(FIBONACCI_DELAYS),
                        delay,
                    )
                    time.sleep(delay)
                else:
                    break
            except Exception as exc:
                with self._stats_lock:
                    self._stats["failed_queries"] += 1
                self.logger.error("Batch failed: %s", exc, exc_info=True)
                raise

        with self._stats_lock:
            self._stats["failed_queries"] += 1
        self.logger.error("Batch failed after retries: %s", last_error)
        raise last_error or RuntimeError("Database batch failed")

    async def execute_async(
        self,
        query: str,
        params: Sequence[Any] = (),
        fetch_results: bool = True,
    ) -> Optional[List[sqlite3.Row]]:
        return await asyncio.to_thread(self.execute, query, params, fetch_results)

    async def execute_many_async(
        self, query: str, params_list: List[Tuple[Any, ...]]
    ) -> int:
        return await asyncio.to_thread(self.execute_many, query, params_list)

    def get_stats(self) -> Dict[str, float]:
        with self._stats_lock:
            stats = dict(self._stats)
        stats["success_rate"] = (
            stats["successful_queries"] / stats["total_queries"] * 100
            if stats["total_queries"]
            else 0.0
        )
        stats["avg_retries"] = (
            stats["total_retries"] / stats["successful_queries"]
            if stats["successful_queries"]
            else 0.0
        )
        return stats

    def close_all(self) -> None:
        try:
            if hasattr(self._local, "conn"):
                self._local.conn.close()
                delattr(self._local, "conn")
            self._closed = True
            self.logger.info("Connection pool closed. Stats: %s", self.get_stats())
        except Exception as exc:
            self.logger.error("Error closing connections: %s", exc, exc_info=True)

    def __del__(self) -> None:
        self.close_all()

    def ping(self) -> None:
        self.execute("SELECT 1", fetch_results=False)


class GridIntelligence:
    """Sovereign storage layer using SQLite with a connection pool."""

    def __init__(
        self,
        db_path: str,
        cache: Optional[CacheBackend] = None,
        cipher_key: Optional[str] = None,
        cache_ttl: int = DEFAULT_CACHE_TTL,
    ) -> None:
        self.db_pool = DatabaseConnectionPool(
            db_path, pool_size=DEFAULT_POOL_SIZE, cipher_key=cipher_key
        )
        self.cache = cache or InMemoryCache()
        self.cache_ttl = cache_ttl
        self.logger = logging.getLogger("namo_nexus.grid")

    def _cache_key(self, scope: str, suffix: Optional[str] = None) -> str:
        return f"grid:{scope}:{suffix}" if suffix else f"grid:{scope}"

    def _set_cache(self, key: str, value: Any) -> None:
        self.cache.set_json(key, value, self.cache_ttl)

    def _invalidate_session_cache(self, session_id: str) -> None:
        self.cache.delete(self._cache_key("session_history", session_id))
        self.cache.delete(self._cache_key("session_alerts", session_id))

    def _invalidate_global_cache(self) -> None:
        self.cache.delete(self._cache_key("global_metrics"))
        self.cache.delete(self._cache_key("recent_sessions"))
        self.cache.delete(self._cache_key("all_alerts"))

    def store_sovereign(self, data: Dict[str, Any]) -> None:
        """Store conversation data; embeddings can be added later."""
        query = """
            INSERT INTO conversations
            (user_id, session_id, message, response, risk_level,
             dharma_score, multimodal_data, timestamp, node_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["user_id"],
            data["session_id"],
            data["message"],
            data["response"],
            data["risk_level"],
            data["dharma_score"],
            json.dumps(data.get("multimodal", {})),
            datetime.now().isoformat(),
            "TH-GRID-01",
        )
        self.db_pool.execute(query, params, fetch_results=False)
        self._invalidate_session_cache(data["session_id"])
        self._invalidate_global_cache()

    def create_crisis_alert(self, data: Dict[str, Any]) -> List[str]:
        empathy_prompts = self._generate_empathy_prompts(data["risk_level"])
        query = """
            INSERT INTO crisis_alerts
            (user_id, session_id, risk_level, alert_type, empathy_prompts, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            data["user_id"],
            data["session_id"],
            data["risk_level"],
            "immediate_intervention",
            json.dumps(empathy_prompts),
            datetime.now().isoformat(),
        )
        self.db_pool.execute(query, params, fetch_results=False)
        self._invalidate_session_cache(data["session_id"])
        self._invalidate_global_cache()
        return empathy_prompts

    async def create_crisis_alert_async(self, data: Dict[str, Any]) -> List[str]:
        return await asyncio.to_thread(self.create_crisis_alert, data)

    def _generate_empathy_prompts(self, risk_level: str) -> List[str]:
        prompts = _LOCALE["database"]["empathy_prompts"]
        return prompts.get(risk_level, prompts["low"])

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        cache_key = self._cache_key("session_history", session_id)
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        query = """
            SELECT message, response, risk_level, dharma_score, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """
        rows = self.db_pool.execute(query, (session_id,))
        result = [
            {
                "message": row[0],
                "response": row[1],
                "risk": row[2],
                "dharma": row[3],
                "time": row[4],
            }
            for row in (rows or [])
        ]
        self._set_cache(cache_key, result)
        return result

    async def get_session_history_async(self, session_id: str) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_session_history, session_id)

    def get_alerts(self, session_id: str) -> List[Dict[str, Any]]:
        cache_key = self._cache_key("session_alerts", session_id)
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        query = """
            SELECT risk_level, empathy_prompts, timestamp, resolved
            FROM crisis_alerts
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """
        rows = self.db_pool.execute(query, (session_id,))
        alerts = []
        for row in rows or []:
            prompts = json.loads(row[1]) if row[1] else []
            alerts.append(
                {
                    "risk": row[0],
                    "prompts": prompts,
                    "time": row[2],
                    "resolved": bool(row[3]),
                }
            )
        self._set_cache(cache_key, alerts)
        return alerts

    async def get_alerts_async(self, session_id: str) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_alerts, session_id)

    def get_global_metrics(self) -> List[Dict[str, Any]]:
        """Fetch historical risk levels and dharma scores for graph visualization."""
        cache_key = self._cache_key("global_metrics")
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        query = """
            SELECT timestamp, risk_level, dharma_score
            FROM conversations
            ORDER BY timestamp ASC
            LIMIT 100
        """
        rows = self.db_pool.execute(query)
        result = [
            {"time": row[0], "risk": row[1], "dharma": row[2]}
            for row in (rows or [])
        ]
        self._set_cache(cache_key, result)
        return result

    async def get_global_metrics_async(self) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_global_metrics)

    def get_recent_sessions(self) -> List[Dict[str, Any]]:
        """Fetch unique recent sessions for the monitor."""
        cache_key = self._cache_key("recent_sessions")
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        query = """
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
        rows = self.db_pool.execute(query)
        result = [
            {"session_id": row[0], "user_id": row[1], "last_active": row[2]}
            for row in (rows or [])
        ]
        self._set_cache(cache_key, result)
        return result

    async def get_recent_sessions_async(self) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_recent_sessions)

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """Fetch all active crisis alerts."""
        cache_key = self._cache_key("all_alerts")
        cached = self.cache.get_json(cache_key)
        if cached is not None:
            return cached
        query = """
            SELECT user_id, session_id, risk_level, timestamp, resolved
            FROM crisis_alerts
            WHERE resolved = 0
            ORDER BY timestamp DESC
        """
        rows = self.db_pool.execute(query)
        result = [
            {
                "user_id": row[0],
                "session_id": row[1],
                "risk": row[2],
                "time": row[3],
                "resolved": bool(row[4]),
            }
            for row in (rows or [])
        ]
        self._set_cache(cache_key, result)
        return result

    async def get_all_alerts_async(self) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_all_alerts)

    def get_stats(self) -> Dict[str, float]:
        return self.db_pool.get_stats()

    def close(self) -> None:
        self.db_pool.close_all()


class NamoDatabase:
    """High-level database interface for triage results (schema required)."""

    def __init__(self, db_path: str = "namo_nexus.db", cipher_key: Optional[str] = None):
        self.pool = DatabaseConnectionPool(
            db_path, pool_size=DEFAULT_POOL_SIZE, cipher_key=cipher_key
        )
        self.logger = logging.getLogger("namo_nexus.namodb")

    async def save_triage_result(self, user_id: str, result: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO triage_results
            (user_id, risk_level, harmonic_score, confidence,
             text_score, voice_score, timestamp, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_id,
            result["risk_level"],
            result["harmonic_score"],
            result["confidence"],
            result.get("analysis", {})
            .get("components", {})
            .get("text", {})
            .get("risk_score"),
            result.get("analysis", {})
            .get("components", {})
            .get("voice", {})
            .get("risk_score"),
            result["timestamp"],
            json.dumps(result),
        )
        try:
            await self.pool.execute_async(query, params, fetch_results=False)
            return True
        except Exception as exc:
            self.logger.error("Failed to save triage result: %s", exc, exc_info=True)
            return False

    async def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM triage_results
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        rows = await self.pool.execute_async(query, (user_id, limit))
        return [dict(row) for row in rows or []]

    def get_pool_stats(self) -> Dict[str, float]:
        return self.pool.get_stats()

    def shutdown(self) -> None:
        self.pool.close_all()
