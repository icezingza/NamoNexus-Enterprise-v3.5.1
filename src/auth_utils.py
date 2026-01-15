import os

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)
EXPECTED_TOKEN = os.getenv("NAMO_NEXUS_TOKEN")


def verify_token(
    creds: HTTPAuthorizationCredentials = Security(security),
) -> bool:
    if EXPECTED_TOKEN is None:
        raise HTTPException(status_code=503, detail="Server mis-configured (no token)")
    if creds is None or creds.credentials != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True
