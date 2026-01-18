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
    grid = GridIntelligence(cipher_key='test' OR '1'='1')
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

#### 4.3 Migrate Legacy Data (Optional)

**ถ้ามีข้อมูลเก่าและต้องการเก็บ:**

```bash
# ใช้ script ที่สร้างไว้ (migrate_legacy_data.py)
python3 migrate_legacy_data.py day3_proof.db

# หรือถ้าชื่อไฟล์อื่น
python3 migrate_legacy_data.py YOUR_OLD_DB_NAME.db
```

**ถ้าไม่ต้องการข้อมูลเก่า:**
```bash
# ลบไฟล์ DB เก่าได้เลย (ระวัง!)
rm -f day3_*.db
rm -f *_day3.db
```

---

### ✅ Day 5: Dependencies & Security Audit

#### 5.1 ติดตั้ง Dependencies ที่ปลอดภัย

**สร้าง requirements ใหม่:**

```bash
cat > requirements-secure.txt << 'EOF'
# Production-ready dependencies - NamoNexus v3.5.1
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
EOF
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
```

#### 5.2 รัน Security Audit

```bash
# ติดตั้งเครื่องมือ audit
pip install pip-audit bandit safety

# ตรวจสอบ dependencies
pip-audit --format=json -o audit-report.json

# ตรวจสอบ code security
bandit -r . -f json -o bandit-report.json

# ดูผลลัพธ์สรุป
echo "=== Security Audit Summary ==="
echo "Dependencies scan: $(pip-audit | grep -c 'VULNERABLE' || echo 0) vulnerabilities"
echo "Code scan: $(bandit -r . | grep -c 'HIGH' || echo 0) high severity issues"
```

---

## 🎯 Phase 3: Testing & Validation (วันที่ 6-7)

### ✅ Day 6: Run Tests

```bash
# รัน tests ทั้งหมด
pytest tests/ -v --tb=short

# ถ้ามี failures ให้ดูสรุป
pytest tests/ --tb=line -q

# รันเฉพาะ tests ที่สำคัญ
pytest tests/unit/test_main_api.py tests/unit/test_audio_triage.py -v
```

### ✅ Day 7: Integration Testing

```bash
# เริ่ม server
python3 main.py &
SERVER_PID=$!
sleep 5

# ทดสอบ health endpoint
curl -f http://localhost:8000/healthz || echo "❌ Health check failed"

# ทดสอบ triage endpoint (ต้องมี token)
curl -X POST http://localhost:8000/triage \
  -H "Authorization: Bearer $NAMO_NEXUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Hello"}' | jq .

# Stop server
kill $SERVER_PID

# รัน stress test (ถ้าพร้อม)
python3 stress_test_triage.py
```

---

## 🎯 Phase 4: Deployment (วันที่ 8-10)

### ✅ Day 8: Staging Deployment

```bash
# Build Docker image
docker build -t namonexus:staging .

# Deploy to staging
docker run -d \
  --name namo-staging \
  -p 8001:8000 \
  -e ENVIRONMENT=staging \
  -e NAMO_NEXUS_TOKEN=$NAMO_NEXUS_TOKEN \
  -e DB_CIPHER_KEY=$DB_CIPHER_KEY \
  namonexus:staging

# ทดสอบ staging
sleep 30
curl -f http://localhost:8001/healthz

# รัน integration tests
pytest tests/integration/ --base-url=http://localhost:8001

# Clean up
docker stop namo-staging
docker rm namo-staging
```

### ✅ Day 9: Production Deployment

```bash
# Build production image
docker build -t namonexus:production .

# Tag for registry
docker tag namonexus:production your-registry.com/namonexus:v3.5.1

# Push to registry
docker push your-registry.com/namonexus:v3.5.1

# Deploy to production (Kubernetes)
kubectl apply -f k8s/ -n namo-production

# ตรวจสอบ deployment
kubectl get pods -n namo-production -w
```

### ✅ Day 10: Monitoring & Go-Live

```bash
# ตั้งค่า monitoring
kubectl apply -f monitoring/ -n namo-production

# ตรวจสอบ logs
kubectl logs -f deployment/namo-nexus -n namo-production

# ทดสอบ production endpoint
export EXTERNAL_IP=$(kubectl get svc namo-nexus -n namo-production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -f https://${EXTERNAL_IP}/healthz

# เปิดให้ user ทดสอบ (beta)
# ติดตาม metrics 24 ชั่วโมง
```

---

## 📈 Rate Limit Guidelines

| Use Case | Rate Limit | Burst | Notes |
|----------|------------|-------|-------|
| **Hospital/Enterprise** | 300 req/min | 50 | รองรับ 50-100 concurrent users |
| **Public API** | 60 req/min | 10 | สำหรับ external developers |
| **Internal/Dev** | 1000 req/min | 200 | ไม่จำกัดใน development |
| **Load Testing** | 5000 req/min | 1000 | ใช้ชั่วคราวเท่านั้น |

---

## 🔄 Rollback Plan

ถ้าพบปัญหาใน production:

```bash
# 1. Rollback deployment
kubectl rollout undo deployment/namo-nexus -n namo-production

# 2. ตรวจสอบ status
kubectl rollout status deployment/namo-nexus -n namo-production

# 3. Restore database (ถ้าจำเป็น)
cp namo_nexus_sovereign.db.backup namo_nexus_sovereign.db

# 4. กลับไปเวอร์ชันเก่า
git checkout HEAD~1
docker-compose up -d --build
```

---

## ✅ Final Checklist

ก่อน go-live ต้องเช็คทุกข้อ:

- [ ] Keys สร้างใหม่ (ไม่ใช่ค่าจาก document)
- [ ] SQL injection แก้ไขแล้ว
- [ ] System dependencies ติดตั้งแล้ว
- [ ] DB migrations applied
- [ ] Tests ทั้งหมดผ่าน (100%)
- [ ] Staging deployment สำเร็จ
- [ ] Rate limit ตั้งค่าถูกต้องตาม use case
- [ ] Monitoring พร้อม
- [ ] Rollback plan tested
- [ ] Team พร้อม support 24/7

---

## 📞 Emergency Contacts

**ถ้าพบปัญหาระหว่าง deployment:**

1. **ดู logs**: `kubectl logs -f deployment/namo-nexus -n namo-production`
2. **ดู metrics**: `kubectl top pods -n namo-production`
3. **ดู events**: `kubectl get events -n namo-production --sort-by='.lastTimestamp'`
4. **Rollback**: ใช้ rollback plan ด้านบน

---

**สร้างโดย**: AI System Architect  
**เวอร์ชัน**: 2.0 Production-Ready  
**อัปเดตล่าสุด**: 18 มกราคม 2026
