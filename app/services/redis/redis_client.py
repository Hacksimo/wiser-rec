import redis
from rq import Queue

# Redis connection setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)
# Queue for interactions
interaction_queue = Queue('interactions', connection=redis_client)