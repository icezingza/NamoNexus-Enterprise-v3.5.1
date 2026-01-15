from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool


def _load_sqlcipher_dbapi():
    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
        return sqlcipher
    except ImportError:
        try:
            import sqlcipher3 as sqlcipher
            return sqlcipher
        except ImportError:
            return None


def get_secure_engine(db_path: str, cipher_key: str):
    """Return SQLAlchemy engine with SQLCipher encryption."""
    if not cipher_key:
        raise ValueError("cipher_key is required for SQLCipher")
    dbapi = _load_sqlcipher_dbapi()
    if dbapi is None:
        raise RuntimeError("SQLCipher DB-API not installed (pysqlcipher3/sqlcipher3)")
    url = f"sqlite:///{db_path}"
    engine = create_engine(
        url,
        module=dbapi,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def set_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        safe_key = cipher_key.replace("'", "''")
        cursor.execute(f"PRAGMA key = '{safe_key}'")
        cursor.execute("PRAGMA cipher = 'aes-256-cfb'")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=30000000000")
        cursor.close()

    return engine
