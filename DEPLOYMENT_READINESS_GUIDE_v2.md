# 🚀 แผนการเตรียมระบบ NamoNexus Enterprise v3.5.1 สำหรับ Production

> **"From Critical to Production-Ready: A Phased Recovery Plan"**
> **Version 2.0** - Updated with Security Hardening & Enterprise Best Practices

## 📊 สรุปสถานะปัจจุบัน

**สถานะ**: 🔴 **ไม่พร้อมสำหรับ Production**  
**ความเสี่ยง**: สูง (มีช่องโหว่ด้านความปลอดภัยและ configuration ผิดพลาด)  
**เวลาประมาณการ**: **10-14 วันทำการ** (รวม staging test และ data migration)  
**Environment**: รองรับทั้ง Linux/macOS และ Windows (PowerShell)

---

## ⚠️ Critical Warnings ก่อนเริ่ม

### 🪤 กับดักที่ต้องระวัง (Production Traps)

1. **SQLCipher Installation** - ถ้าไม่ติดตั้ง system dependencies ก่อน `pip install` จะพังแน่นอน
2. **Data Migration** - DB เก่า (unencrypted) กับ DB ใหม่ (encrypted) ต้องมีแผนย้ายข้อมูล
3. **Rate Limit** - 60 req/min อาจโหดเกินไปสำหรับโรงพยาบาลที่มีผู้ใช้หลายคน
4. **Token Reuse** - อย่าใช้ค่า token ตัวอย่างใน document โดยตรง

---

## 🎯 Phase 0: Pre-Deployment Preparation (วันที่ 0)

### ✅ สร้าง Secret Keys สำหรับแต่ละ Environment

**สำคัญ**: สร้างคีย์ใหม่ทุกครั้งที่ deploy แต่ละ environment (dev/staging/production)

```bash
# Linux/macOS: สร้างคีย์แบบสุ่ม
python3 -c "import secrets; print('NAMO_NEXUS_TOKEN=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('DB_CIPHER_KEY=' + secrets.token_urlsafe(32))"

# Windows (PowerShell): สร้างคีย์แบบสุ่ม
python -c "import secrets; print('NAMO_NEXUS_TOKEN=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('DB_CIPHER_KEY=' + secrets.token_urlsafe(32))"

# บันทึกค่าเหล่านี้ไว้ใน Password Manager (Bitwarden, 1Password)
# อย่า commit ลง Git!
```

**ตัวอย่างผลลัพธ์ที่ควรได้:**
```
NAMO_NEXUS_TOKEN=YOUR_NAMO_NEXUS_TOKEN_HERE  # แทนที่ด้วยค่าจริง
DB_CIPHER_KEY=YOUR_DB_CIPHER_KEY_HERE        # แทนที่ด้วยค่าจริง
```

### ✅ สำรองข้อมูลเดิม (ถ้ามี)

```bash
# Linux/macOS
cp namo_nexus_sovereign.db namo_nexus_sovereign.db.backup.$(date +%Y%m%d)
cp *.env *.env.backup.$(date +%Y%m%d)

# Windows
Copy-Item namo_nexus_sovereign.db "namo_nexus_sovereign.db.backup.$(Get-Date -Format 'yyyyMMdd')"
Copy-Item *.env "env.backup.$(Get-Date -Format 'yyyyMMdd')"
```

---

## 🎯 Phase 1: Critical Security Fixes (วันที่ 1-2)

### ✅ Day 1: Security Hardening

#### 1.1 แก้ไข SQL Injection (P0 - Critical)

**เปิดไฟล์ `database.py` และแก้ไข:**

```python
# บรรทัด 86-87 (เดิม):
# cursor.execute(f"PRAGMA key = '{safe_key}'")

# เปลี่ยนเป็น (ใหม่):
cursor.execute("PRAGMA key = ?", (self.cipher_key,))
```

**ตรวจสอบว่าแก้ไขถูกต้อง:**

```bash
# Linux/macOS
python3 -c "
import sqlite3
from database import GridIntelligence

# ลองใส่คีย์ที่มี single quote (potential SQL injection)
try:
    grid = GridIntelligence(cipher_key=\"test' OR '1'='1\")
    with grid.get_connection() as conn:
        print('❌ ยังไม่ปลอดภัย: สามารถใช้คีย์ที่มี quote ได้')
except Exception as e:
    if 'sql' in str(e).lower() or 'syntax' in str(e).lower():
        print('❌ ยังไม่ปลอดภัย: เกิด SQL error')
    else:
        print('✅ ปลอดภัย: จับ quote ใน parameter ได้ถูกต้อง')
"

# Windows (PowerShell)
python -c "
import sqlite3
from database import GridIntelligence

try:
    grid = GridIntelligence(cipher_key='test' OR '1'='1')
    with grid.get_connection() as conn:
        print('❌ ยังไม่ปลอดภัย')
except Exception as e:
    print('✅ ปลอดภัย: Parameterized query ทำงานได้')
"
```

#### 1.2 แยก Database Cipher Key จาก Auth Token (P0 - Critical)

**แก้ไขไฟล์ `.env` หรือ `.env.production`:**

```bash
# ลบหรือคอมเมนต์ค่าเดิมถ้ามี
# DB_CIPHER_KEY=DwTuv-cSiI2XwdQ4FoaNih5qGUUbru_yrD3-IvJKUw8=  ❌ อย่าใช้ค่านี้

# เพิ่มค่าใหม่ (สร้างจาก Phase 0)
DB_CIPHER_KEY=YOUR_DB_CIPHER_KEY_HERE
NAMO_NEXUS_TOKEN=YOUR_NAMO_NEXUS_TOKEN_HERE
```

**ตรวจสอบ configuration:**

```bash
# สร้าง validation script
python3 << 'EOF'
import os
import sys

REQUIRED_VARS = [
    "NAMO_NEXUS_TOKEN",
    "DB_CIPHER_KEY",
    "DATABASE_URL"
]

missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    print(f"❌ Missing variables: {missing}")
    sys.exit(1)

# ตรวจสอบว่าไม่ได้ใช้ค่าเดียวกัน
if os.getenv("NAMO_NEXUS_TOKEN") == os.getenv("DB_CIPHER_KEY"):
    print("⚠️  Warning: Token และ Cipher Key เป็นค่าเดียวกัน ควรใช้ค่าต่างกัน")
    sys.exit(1)

print("✅ All configurations validated successfully")
print(f"   Token length: {len(os.getenv('NAMO_NEXUS_TOKEN'))} chars")
print(f"   Cipher key length: {len(os.getenv('DB_CIPHER_KEY'))} chars")
sys.exit(0)
EOF
```

#### 1.3 ตั้งค่า Rate Limit ตาม Use Case (P1 - High)

**⚠️ อย่าใช้ 60 req/min สำหรับโรงพยาบาล!**

เลือกตาม scenario ของคุณ:

**Scenario A: Hospital/Enterprise (แนะนำ)**
```bash
# Linux/macOS
sed -i 's/RATE_LIMIT_PER_MINUTE=.*/RATE_LIMIT_PER_MINUTE=300/' .env
sed -i 's/RATE_LIMIT_BURST=.*/RATE_LIMIT_BURST=50/' .env

# Windows PowerShell
(Get-Content .env) -replace 'RATE_LIMIT_PER_MINUTE=.*', 'RATE_LIMIT_PER_MINUTE=300' | Set-Content .env
(Get-Content .env) -replace 'RATE_LIMIT_BURST=.*', 'RATE_LIMIT_BURST=50' | Set-Content .env
```

**Scenario B: Public API (เข้มงวด)**
```bash
# Linux/macOS
sed -i 's/RATE_LIMIT_PER_MINUTE=.*/RATE_LIMIT_PER_MINUTE=60/' .env
sed -i 's/RATE_LIMIT_BURST=.*/RATE_LIMIT_BURST=10/' .env

# Windows PowerShell
(Get-Content .env) -replace 'RATE_LIMIT_PER_MINUTE=.*', 'RATE_LIMIT_PER_MINUTE=60' | Set-Content .env
(Get-Content .env) -replace 'RATE_LIMIT_BURST=.*', 'RATE_LIMIT_BURST=10' | Set-Content .env
```

**Scenario C: Internal Service (ไม่จำกัดใน Dev)**
```bash
# Linux/macOS
sed -i 's/RATE_LIMIT_PER_MINUTE=.*/RATE_LIMIT_PER_MINUTE=1000/' .env
sed -i 's/RATE_LIMIT_BURST=.*/RATE_LIMIT_BURST=200/' .env

# Windows PowerShell
(Get-Content .env) -replace 'RATE_LIMIT_PER_MINUTE=.*', 'RATE_LIMIT_PER_MINUTE=1000' | Set-Content .env
(Get-Content .env) -replace 'RATE_LIMIT_BURST=.*', 'RATE_LIMIT_BURST=200' | Set-Content .env
```

#### 1.4 เพิ่ม Allowed Audio Types

```python
# แก้ไข main.py บรรทัด 330

ALLOWED_AUDIO_TYPES = {
    "audio/wav", "audio/mpeg", "audio/flac", 
    "audio/ogg", "audio/webm", "audio/aac", "audio/mp4"
}
```

---

### ✅ Day 2: Audit Logging & Input Validation

#### 2.1 แก้ไข Audit Middleware

```python
# แก้ไข src/audit_middleware.py บรรทัด 43-44

# เดิม:
ip_addr="",
user_agent="",

# ใหม่:
ip_addr=request.client.host if request.client else "",
user_agent=request.headers.get("user-agent", "")[:200],  # จำกัดขนาด
```

#### 2.2 เพิ่ม Input Size Validation

```python
# แก้ไข src/schemas_day2.py
from pydantic import BaseModel, conlist, confloat, constr

class MultiModalAnalysis(BaseModel):
    # จำกัดขนาดเพื่อป้องกัน DoS
    message: constr(max_length=5000)  # จำกัด message 5000 ตัวอักษร
    voice_features: Optional[conlist(confloat(), max_items=2000)] = None  # Max 2000 features
    facial_features: Optional[conlist(confloat(), max_items=1000)] = None  # Max 1000 features
```

---

## 🎯 Phase 2: Configuration & Database (วันที่ 3-5)

### ✅ Day 3: Fix Configuration

#### 3.1 ตรวจสอบ Pre-requisites (สำคัญ!)

```bash
# ตรวจสอบว่า Python version ถูกต้อง
python3 --version  # ต้องเป็น 3.8+

# ตรวจสอบว่ามี SQLite3 หรือไม่
python3 -c "import sqlite3; print(f'SQLite version: {sqlite3.sqlite_version}')"

# Linux/macOS: ตรวจสอบว่า sqlcipher ติดตั้งหรือยัง
which sqlcipher || echo "❌ sqlcipher ไม่ได้ติดตั้ง ต้อง install ก่อนด้านล่าง"
```

#### 3.2 ติดตั้ง System Dependencies (CRITICAL!)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libsqlcipher-dev \
    pkg-config \
    python3-dev

# ตรวจสอบว่าติดตั้งสำเร็จ
pkg-config --modversion sqlcipher || echo "❌ ติดตั้งไม่สำเร็จ"
```

**macOS (Homebrew):**
```bash
brew install sqlcipher pkg-config

# ตรวจสอบ
pkg-config --modversion sqlcipher
```

**Windows:**
```powershell
# ดาวน์โหลด SQLCipher สำหรับ Windows จาก: https://www.zetetic.net/sqlcipher/
# ติดตั้งแล้วเพิ่มใน PATH

# ตรวจสอบ
sqlcipher --version
```

#### 3.3 แก้ไข alembic.ini

```bash
# Linux/macOS
sed -i 's|sqlalchemy.url = driver://user:pass@localhost/dbname|sqlalchemy.url = sqlite:///namo_nexus_sovereign.db|' alembic.ini

# Windows PowerShell
(Get-Content alembic.ini) -replace 'sqlalchemy.url = driver://user:pass@localhost/dbname', 'sqlalchemy.url = sqlite:///namo_nexus_sovereign.db' | Set-Content alembic.ini

# ตรวจสอบ
grep "sqlalchemy.url" alembic.ini
```

#### 3.4 แก้ไข docker-compose.yml (Version ที่ถูกต้อง)

```yaml
# version 2.0 - ปรับ port และเพิ่ม healthcheck
version: "3.8"
services:
  namo-nexus:
    build: .
    container_name: namo_enterprise_v3
    restart: always
    ports:
      - "8000:8000"  # เปลี่ยนจาก 8080:8080 เพื่อให้สอดคล้องกับ .env
    volumes:
      - ./data:/app/data
    environment:
      - PORT=8000
      - NAMO_NEXUS_TOKEN=${NAMO_NEXUS_TOKEN}
      - DB_CIPHER_KEY=${DB_CIPHER_KEY}
      - DATABASE_URL=sqlite:///app/data/namo_nexus_sovereign.db
      - DB_PATH=/app/data/namo_nexus_sovereign.db
      - RATE_LIMIT_PER_MINUTE=${RATE_LIMIT_PER_MINUTE:-300}
      - RATE_LIMIT_BURST=${RATE_LIMIT_BURST:-50}
      - CORS_ALLOW_ORIGINS=${CORS_ALLOW_ORIGINS:-http://localhost:3000}
      - LOG_LEVEL=INFO
      - ENVIRONMENT=production
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

### ✅ Day 4: Database Migration

#### 4.1 ตรวจสอบสถานะฐานข้อมูลปัจจุบัน

```bash
# สร้าง migration status script
python3 << 'EOF'
import sqlite3
import os

db_path = os.getenv("DB_PATH", "namo_nexus_sovereign.db")

# ถ้าไฟล์ DB ใหม่ไม่มี, สร้างใหม่
if not os.path.exists(db_path):
    print(f"❌ DB not found: {db_path}")
    print("   จะสร้าง DB ใหม่เมื่อรัน migrations")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ดู tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✅ DB found: {db_path}")
    print(f"   Tables: {tables}")
    
    # ดูขนาด
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")
    
    conn.close()
EOF
```

#### 4.2 Apply Migrations

```bash
# ตรวจสอบ migration history
alembic history

# Apply migrations (ถ้ายังไม่ได้ทำ)
alembic upgrade head

# ตรวจสอบว่า apply สำเร็จ
alembic current
```

#### 4.3 อัปเกรด Database Schema (ถ้ามี table เก่า)

```bash
# ถ้ามีตารางเดิม (conversations, crisis_alerts) ที่ไม่ได้สร้างผ่าน migrations
python3 << 'EOF'
import sqlite3
import os

# เชื่อมต่อ DB เก่า (ถ้ามี)
old_db = "day3_proof.db"  # หรือชื่ออื่นตามที่มี
new_db = os.getenv("DB_PATH", "namo_nexus_sovereign.db")

if os.path.exists(old_db):
    print(f"Found old DB: {old_db}")
    print("ต้องย้ายข้อมูลหรือไม่? (y/n)")
    response = input()
    
    if response.lower() == 'y':
        conn_old = sqlite3.connect(old_db)
        cursor_old = conn_old.cursor()
        
        # ดึงข้อมูลจากตารางเก่า
        cursor_old.execute("SELECT * FROM conversations LIMIT 5")
        sample = cursor_old.fetchall()
        print(f"Sample data: {sample}")
        
        print("⚠️  ต้องสร้าง migration script เพิ่มเติม")
        print("    ดูส่วน 'Data Migration Script' ด้านล่าง")
        
        conn_old.close()
else:
    print("✅ ไม่มี DB เก่า เริ่มต้นใหม่ได้เลย")
EOF
```

#### 4.4 Data Migration Script (Optional - ถ้าต้องการเก็บข้อมูลเก่า)

```python
# migrate_legacy_data.py
import sqlite3
import os
from database import GridIntelligence

def migrate_data(old_db_path="day3_proof.db", new_db_path=None):
    """
    ย้ายข้อมูลจาก SQLite ธรรมดาไป SQLCipher (encrypted)
    """
    if new_db_path is None:
        new_db_path = os.getenv("DB_PATH", "namo_nexus_sovereign.db")
    
    if not os.path.exists(old_db_path):
        print(f"❌ Old DB not found: {old_db_path}")
        return False
    
    print(f"Opening old DB: {old_db_path}")
    conn_old = sqlite3.connect(old_db_path)
    cursor_old = conn_old.cursor()
    
    # สร้าง GridIntelligence ใหม่ (encrypted)
    cipher_key = os.getenv("DB_CIPHER_KEY")
    if not cipher_key:
        print("❌ DB_CIPHER_KEY not set")
        return False
    
    print(f"Creating encrypted DB: {new_db_path}")
    grid = GridIntelligence(db_path=new_db_path, cipher_key=cipher_key)
    
    with grid.get_connection() as conn_new:
        cursor_new = conn_new.cursor()
        
        # ดึงรายชื่อตารางจาก DB เก่า
        cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor_old.fetchall()]
        print(f"Found tables: {tables}")
        
        migrated_count = 0
        for table in tables:
            try:
                # ดึงข้อมูล
                cursor_old.execute(f"SELECT * FROM {table}")
                rows = cursor_old.fetchall()
                
                # ดึง column names
                cursor_old.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor_old.fetchall()]
                
                # สร้าง INSERT statement
                placeholders = ",".join(["?"]*len(columns))
                insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                
                # อินเสิร์ทข้อมูล
                for row in rows:
                    cursor_new.execute(insert_sql, row)
                
                migrated_count += len(rows)
                print(f"   Migrated {len(rows)} rows from {table}")
                
            except Exception as e:
                print(f"   ⚠️  Skipped {table}: {e}")
        
        conn_new.commit()
    
    conn_old.close()
    print(f"✅ Migration complete: {migrated_count} rows migrated")
    return True

if __name__ == "__main__":
    import sys
    old_db = sys.argv[1] if len(sys.argv) > 1 else "day3_proof.db"
    migrate_data(old_db)
```

**ใช้งาน:**
```bash
python3 migrate_legacy_data.py day3_proof.db
```

---

### ✅ Day 5: Dependencies & Security Audit

#### 5.1 ติดตั้ง Dependencies ที่ปลอดภัย

**สร้าง requirements ใหม่:**

```bash
# requirements-secure.txt (Production-Ready)
fastapi==0.115.2                    # อัปเดตจาก 0.109.0 (CVE แก้ไขแล้ว)
uvicorn[standard]==0.32.0           # อัปเดตจาก 0.27.0
pydantic==2.6.4                     # อัปเดตจาก 2.6.0
pydantic-settings>=2.2.1            # เพิ่ม (ขาดในเดิม)
sqlalchemy>=2.0.30
alembic>=1.13.0                     # เพิ่ม (ขาดในเดิม)
python-jose[cryptography]>=3.3.0    # เพิ่ม (ขาดในเดิม)
passlib[bcrypt]>=1.7.4              # เพิ่ม (ขาดในเดิม)
python-dotenv>=1.0.0                # เพิ่ม (ขาดในเดิม)
aiofiles==23.2.1
python-multipart==0.0.9
requests>=2.32.0                    # อัปเดตจาก 2.31.0 (CVE-2024-35195)
numpy>=1.26.4                       # อัปเดตจาก 1.26.3 (CVE-2024-34791)
redis==5.0
prometheus-client==0.20
bleach==6.0
openai-whisper>=20231117            # เปลี่ยนจาก whisper-openai (ถูกต้อง)
librosa==0.10.1
slowapi==0.1.9

# Platform-specific (อย่าแก้ไข)
pysqlcipher3==1.0.3; platform_system != "Windows"
sqlcipher3>=0.6.2; platform_system == "Windows"
```

**ติดตั้ง:**

```bash
# Linux/macOS - ต้องติดตั้ง system deps ก่อน (ดู Day 3.2)
pip install --upgrade pip setuptools wheel
pip install -r requirements-secure.txt

# Windows
pip install --upgrade pip setuptools wheel
pip install -r requirements-secure.txt

# ตรวจสอบว่าติดตั้งสำเร็จ
python3 -c "
import fastapi, pydantic, requests, numpy
print('✅ Core packages installed')
print(f'FastAPI: {fastapi.__version__}')
print(f'Requests: {requests.__version__}')
"