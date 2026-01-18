# NamoNexus Enterprise v3.5.2 — Technical Manual

> **Sovereign AI Mental Health Infrastructure with SQLCipher Encryption & i18n Support**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Setup Guide](#setup-guide)
3. [Localization Guide](#localization-guide)
4. [Security Note](#security-note)

---

## Architecture Overview

### System Components

NamoNexus Enterprise v3.5.2 is built on a **Sovereign AI** architecture, meaning all data processing and storage remain under your complete control. The system integrates three core pillars:

```
┌─────────────────────────────────────────────────────────────────┐
│                    NamoNexus Enterprise v3.5.2                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   FastAPI   │───▶│  Harmonic   │───▶│   GridIntelligence  │  │
│  │   Endpoints │    │  Governor   │    │   (Data Layer)      │  │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘  │
│                                                   │             │
│                                                   ▼             │
│                          ┌────────────────────────────────────┐ │
│                          │    DatabaseConnectionPool          │ │
│                          │    ┌─────────────────────────┐     │ │
│                          │    │  SQLCipher (AES-256)    │     │ │
│                          │    │  + WAL Mode             │     │ │
│                          │    │  + Connection Pooling   │     │ │
│                          │    └─────────────────────────┘     │ │
│                          └────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      i18n Layer                             ││
│  │  src/i18n.py ──▶ src/locales/*.json                         ││
│  │  (LRU Cached)    (th.json, en.json, ...)                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 1. Sovereign AI Engine

The `HarmonicGovernor` in `core_engine.py` orchestrates all AI operations:

- **Text Analysis**: Risk assessment with Thai language-specific patterns
- **Voice Analysis**: Pitch, energy, and speech rate extraction via `voice_extractor.py`
- **Multimodal Fusion**: Combines text, voice, and facial features for comprehensive triage

### 2. SQLCipher Encrypted Database

The `DatabaseConnectionPool` in `database.py` provides:

| Feature | Implementation |
|---------|----------------|
| **Encryption** | AES-256-CFB via SQLCipher |
| **Journal Mode** | WAL (Write-Ahead Logging) for concurrent reads |
| **Connection Pooling** | Thread-safe with `BoundedSemaphore` |
| **Retry Logic** | Fibonacci backoff (1, 1, 2, 3, 5, 8, 13, 21 seconds) |
| **Parameterized Queries** | All queries use `?` placeholders |

**Key initialization flow:**

```python
# database.py lines 78-93
def _connect(self, timeout: float = DB_TIMEOUT_SECONDS) -> sqlite3.Connection:
    if self.cipher_key:
        conn = sqlcipher.connect(self.db_path, ...)
        cursor = conn.cursor()
        # Parameterized query prevents SQL injection
        cursor.execute("PRAGMA key = ?", (self.cipher_key,))
        cursor.execute("PRAGMA cipher = 'aes-256-cfb'")
```

### 3. Internationalization (i18n)

The `src/i18n.py` module provides locale-based content:

```python
# src/i18n.py
@lru_cache(maxsize=4)
def load_locale(locale: str | None = None) -> Dict[str, Any]:
    path = LOCALES_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)
```

The default locale is set via `NAMO_NEXUS_LOCALE` environment variable (default: `th`).

---

## Setup Guide

### Prerequisites

- Python 3.10 or higher
- SQLCipher library installed on your system
- pip or uv package manager

### Step 1: Clone and Install Dependencies

```bash
git clone https://github.com/your-org/NamoNexus-Enterprise-v3.5.1.git
cd NamoNexus-Enterprise-v3.5.1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Generate Security Keys

Generate cryptographically secure keys for production:

```bash
# Generate NAMO_NEXUS_TOKEN (API authentication)
python -c "import secrets; print('NAMO_NEXUS_TOKEN=' + secrets.token_urlsafe(32))"

# Generate DB_CIPHER_KEY (database encryption) - MUST be different from token
python -c "import secrets; print('DB_CIPHER_KEY=' + secrets.token_urlsafe(32))"
```

**Example output:**

```
NAMO_NEXUS_TOKEN=xK7mN9pQ2rS5tUvW8xYzA3bC6dE0fGhI_jKlMnOp
DB_CIPHER_KEY=qR4sT7uV0wX2yZaB5cD8eFgH1iJkL3mNoPqRsTuV
```

> ⚠️ **CRITICAL**: Never use the same value for both `NAMO_NEXUS_TOKEN` and `DB_CIPHER_KEY`. The token is exposed in API headers, while the cipher key protects your database.

### Step 3: Configure Environment Variables

Copy the example and fill in your generated keys:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Required: API Authentication Token
NAMO_NEXUS_TOKEN=your_generated_token_here

# Required: Database Encryption Key (MUST be different from token)
DB_CIPHER_KEY=your_generated_cipher_key_here

# Core Settings
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///namo_nexus_sovereign.db
DB_PATH=data/namo_nexus_sovereign.db

# Rate Limiting (adjust for your workload)
RATE_LIMIT_PER_MINUTE=300    # Standard API
RATE_LIMIT_BURST=50          # Burst allowance

# CORS (comma-separated origins)
CORS_ALLOW_ORIGINS=http://localhost:3000,https://your-domain.com

# Localization
NAMO_NEXUS_LOCALE=th         # Options: th, en

# Voice Analysis (optional)
ENABLE_TRANSCRIPTION=true
WHISPER_MODEL=base           # Options: tiny, base, small, medium, large
```

### Step 4: Initialize Database

Run migrations to set up the database schema:

```bash
# Using Alembic
alembic upgrade head

# Or use the migration helper script
python run_migration.py
```

### Step 5: Start the Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 6: Verify Installation

```bash
# Health check
curl http://localhost:8000/healthz

# Test triage endpoint
curl -X POST http://localhost:8000/triage \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"สวัสดีครับ"}'
```

---

## Localization Guide

NamoNexus supports multiple languages through JSON locale files stored in `src/locales/`.

### Current Locales

| Locale | File | Description |
|--------|------|-------------|
| Thai | `src/locales/th.json` | Default language with complete translations |

### Adding a New Language

#### Step 1: Create the Locale File

Create a new JSON file in `src/locales/`:

```bash
# Example: Adding English
touch src/locales/en.json
```

#### Step 2: Copy and Translate the Structure

Use `th.json` as a template. The file must contain these top-level keys:

```json
{
  "responses": {
    "greeting": {
      "compassionate": "I sense you're going through a difficult time",
      "supportive": "Hello, I'm here to listen",
      "default": "Hello"
    },
    "main": {
      "severe": "I see you're facing a very difficult moment. You're not alone. May I help you?",
      "moderate": "Thank you for trusting me with this. I understand how you feel.",
      "low": "I'm happy to chat with you."
    },
    "dharma_note_format": "(Principles: {principles})"
  },
  "core_engine": {
    "core_principles": { ... },
    "safety_constraints": { ... },
    "text_patterns": { ... }
  },
  "database": {
    "empathy_prompts": {
      "severe": ["..."],
      "moderate": ["..."],
      "low": ["..."]
    }
  },
  "config": {
    "critical_keywords_th": ["..."]
  },
  "dharma_service": { ... }
}
```

#### Step 3: Update Critical Keywords

The `config.critical_keywords_th` array contains keywords that trigger crisis alerts. For a new language, create a corresponding key:

```json
{
  "config": {
    "critical_keywords_en": [
      "kill myself",
      "suicide",
      "want to die",
      "hopeless",
      "end my life"
    ]
  }
}
```

#### Step 4: Set the Default Locale

Update your `.env` file:

```env
NAMO_NEXUS_LOCALE=en
```

Or set it dynamically in code:

```python
from src.i18n import load_locale

# Load specific locale
locale_data = load_locale("en")

# Access translations
greeting = locale_data["responses"]["greeting"]["default"]
```

#### Step 5: Test Your Translations

```python
# test_locale.py
from src.i18n import load_locale

def test_new_locale():
    locale = load_locale("en")
    assert "responses" in locale
    assert "greeting" in locale["responses"]
    print("✅ Locale validation passed")

if __name__ == "__main__":
    test_new_locale()
```

### Locale File Best Practices

1. **Preserve structure**: Keep the exact same JSON structure as `th.json`
2. **Use UTF-8-BOM**: Save files with `utf-8-sig` encoding for special characters
3. **Test keywords**: Ensure critical safety keywords are culturally appropriate
4. **Cache awareness**: Locales are LRU-cached; restart server after changes

---

## Security Note

### Why Parameterized Queries?

SQL Injection is one of the most critical vulnerabilities in web applications. NamoNexus Enterprise enforces **parameterized queries** throughout the codebase to prevent this attack vector.

#### The Problem: String Interpolation

**❌ DANGEROUS — Never do this:**

```python
# This allows SQL injection
cipher_key = user_input  # Could be: "'; DROP TABLE users; --"
cursor.execute(f"PRAGMA key = '{cipher_key}'")
```

An attacker could input:

```
'; DROP TABLE conversations; --
```

This transforms the query into:

```sql
PRAGMA key = ''; DROP TABLE conversations; --'
```

#### The Solution: Parameterized Queries

**✅ SECURE — Always use this pattern:**

```python
# database.py line 91
cursor.execute("PRAGMA key = ?", (self.cipher_key,))
```

The database driver treats the parameter as **data**, not as **SQL code**, preventing injection attacks.

### Maintaining Security Standards

#### 1. Code Review Checklist

Before merging any database-related code, verify:

- [ ] All `execute()` calls use `?` placeholders
- [ ] No string formatting (`f""`, `.format()`, `%`) in SQL queries
- [ ] Parameters are passed as tuples: `(param,)` or `(param1, param2)`

#### 2. Automated Scanning

Run the audit guard before commits:

```bash
python audit_guard.py
```

This scans for:

- Direct `sqlite3.connect()` calls (should use connection pool)
- SQL injection patterns
- Hardcoded keys or tokens

#### 3. Query Patterns

| Pattern | Status | Example |
|---------|--------|---------|
| `cursor.execute("SELECT * FROM x WHERE id = ?", (id,))` | ✅ Secure | Parameterized |
| `cursor.execute(f"SELECT * FROM x WHERE id = {id}")` | ❌ Vulnerable | String formatting |
| `cursor.execute("SELECT * FROM x WHERE id = " + id)` | ❌ Vulnerable | Concatenation |

#### 4. Secure Defaults in DatabaseConnectionPool

The connection pool enforces security at multiple layers:

```python
class DatabaseConnectionPool:
    def _connect(self, timeout: float) -> sqlite3.Connection:
        if self.cipher_key:
            # Validate key doesn't contain injection characters
            if "'" in self.cipher_key:
                raise ValueError("Cipher key cannot contain single quotes")
            
            # Use parameterized query for key setting
            cursor.execute("PRAGMA key = ?", (self.cipher_key,))
            cursor.execute("PRAGMA cipher = 'aes-256-cfb'")
```

### Security Configuration Checklist

| Setting | Recommended Value | Purpose |
|---------|-------------------|---------|
| `DB_CIPHER_KEY` | 32+ character random | Database encryption |
| `NAMO_NEXUS_TOKEN` | 32+ character random | API authentication |
| `RATE_LIMIT_PER_MINUTE` | 60-300 | Prevent abuse |
| `RATE_LIMIT_BURST` | 10-50 | Handle traffic spikes |
| `CORS_ALLOW_ORIGINS` | Specific origins | Prevent CSRF |
| `ENVIRONMENT` | `production` | Enable security features |

---

## Summary

NamoNexus Enterprise v3.5.2 provides:

- **Sovereign Architecture**: Complete data control with encrypted local storage
- **SQLCipher Integration**: AES-256 encryption with parameterized queries
- **i18n Support**: Extensible localization through JSON locale files
- **Security-First Design**: SQL injection prevention at the architectural level

For questions or contributions, please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) guide.

---

*Document Version: 3.5.2*  
*Last Updated: January 2026*
