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
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified_claims.get("iss")
        
        if not issuer:
            raise HTTPException(status_code=401, detail="Missing issuer in token")
            
        jwks = get_jwks(issuer)
        
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
                
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token kid")
            
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=issuer
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")

from app.db.session import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
