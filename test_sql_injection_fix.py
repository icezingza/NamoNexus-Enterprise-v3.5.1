
import sqlite3
try:
    import sqlcipher3
    print(sqlcipher3.version)
except ImportError:
    print("sqlcipher3 not found")
from database import GridIntelligence

try:
    grid = GridIntelligence(db_path="test_injection.db", cipher_key="test' OR '1'='1")
    with grid.db_pool.get_connection() as conn:
        print("❌ SQL Injection ยังไม่ถูกแก้ไข")
except ValueError as e:
    print(f"✅ SQL Injection ถูกแก้ไขแล้ว: {e}")
except Exception as e:
    print(f"❌ Test failed with unexpected error: {e}")
