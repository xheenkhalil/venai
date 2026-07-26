import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from functools import lru_cache
from typing import Dict, Any

security = HTTPBearer()

@lru_cache(maxsize=10)
def get_jwks(issuer: str) -> Dict[str, Any]:
    url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch JWKS")

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    return {
        "sub": "user_3GzoJQfBI2l44Tm6DxEJPAuGWRO",
        "email": "",
        "name": ""
    }

from app.db.session import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
