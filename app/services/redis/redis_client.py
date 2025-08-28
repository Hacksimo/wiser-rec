# app/services/redis_client.py
import os
import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB   = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# decode_responses False to store binary pickles
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
