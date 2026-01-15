from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool


def get_secure_engine(db_path: str, cipher_key: str):
    """Return SQLAlchemy engine with SQLCipher encryption."""
    if not cipher_key:
        raise ValueError("cipher_key is required for SQLCipher")
    url = f"sqlite+pysqlcipher://:{cipher_key}@/{db_path}?cipher=aes-256-cfb"
    engine = create_engine(
        url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def set_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=30000000000")
        cursor.close()

    return engine
