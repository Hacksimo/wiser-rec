# app/services/redis/redis_queue.py
from rq import Queue
from app.services.redis.redis_client import redis_conn

interaction_queue = Queue("interactions", connection=redis_conn)
