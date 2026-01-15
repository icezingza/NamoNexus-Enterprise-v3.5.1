## Data-at-Rest Encryption & Audit (Day-3)
- SQLite encrypted with SQLCipher (AES-256-CFB)
- Encryption key derived from ENV (rotatable)
- WAL + hardening pragmas for performance and durability
- Immutable audit log (append-only) per API call
- Log fields: user_id, endpoint, IP, user-agent, payload, timestamp
- Verified: opening DB without key -> "file is not a database"
