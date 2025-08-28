# app/deps/api_key.py
from fastapi import HTTPException, Header, status, Request
from typing import Optional
from app.services.redis.redis_client import redis_conn

REDIS_PREFIX = "reco:api_key:"   # keys stored as reco:api_key:<key> 

def require_api_key(x_api_key: Optional[str] = Header(None)):
    """
    FastAPI dependency. Raise 401 if missing, 403 if invalid.
    """
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-KEY header")
    # check key existence in redis
    if not redis_conn.exists(REDIS_PREFIX + x_api_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return x_api_key
