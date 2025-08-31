# app/services/redis_model.py
import pickle
import zlib
from typing import Optional
from app.services.redis.redis_client import redis_conn
from app.services.mf import MatrixFactorization

MODEL_KEY = "mf_model_v1"
LOCK_KEY = "mf_model_lock_v1"

def save_model(model: MatrixFactorization, key: str = MODEL_KEY):
    raw = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
    compressed = zlib.compress(raw)
    redis_conn.set(key, compressed)

def load_model(key: str = MODEL_KEY) -> Optional[MatrixFactorization]:
    data = redis_conn.get(key)
    if data is None:
        return None
    raw = zlib.decompress(data)
    model = pickle.loads(raw)
    return model

def get_lock(blocking: bool = True, timeout: int = 30):
    """
    Returns a redis.lock.Lock object; use as context manager or call acquire/release.
    """
    return redis_conn.lock(LOCK_KEY, blocking=blocking, timeout=timeout)

def reset_model(key: str = MODEL_KEY):
    """
    Deletes the stored model from Redis.
    """
    redis_conn.delete(key)
