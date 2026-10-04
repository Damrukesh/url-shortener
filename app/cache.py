import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
CACHE_TTL = 3600  # seconds