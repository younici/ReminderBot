import os

import redis.asyncio as redis

from db.orm.session import AsyncSessionLocal
from db.orm.models.user import User
from sqlalchemy import select

_redis_client: redis.Redis | None = None

async def init_redis():
    global _redis_client
    redis_url = os.getenv("REDIS_URL")

    print(f"redis url {redis_url}")

    _redis_client = redis.from_url(redis_url, decode_responses=True)

    try:
        await _redis_client.ping()
    except Exception as e:
        print(f"redis err: {e}")
        _redis_client = None

    return _redis_client

def get_redis_client() -> redis.Redis:
    return _redis_client

async def preload_keys():
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User))

        users = res.scalars().all()

        if users:
            for usr in users:
                await _redis_client.set(f"user:{usr.tg_id}:lang", usr.lang_code)