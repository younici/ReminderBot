import os

import redis.asyncio as redis

_redis_client: redis.Redis | None = None

async def init_redis():
    global _redis_client
    redis_url = os.getenv("REDIS_URL")

    _redis_client = redis.from_url(redis_url, decode_responses=True)

    try:
        await _redis_client.ping()
    except Exception as e:
        print(f"redis err: {e}")
        _redis_client = None

    return _redis_client

def get_redis_client() -> redis.Redis:
    return _redis_client
