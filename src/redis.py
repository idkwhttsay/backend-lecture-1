import redis
from src.config import settings

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

def check_redis_connection():
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False

async def set_value(key: str, value: str, expire: int = None):
    if expire:
        await redis_client.setex(key, expire, value)
    else:
        await redis_client.set(key, value)

async def get_value(key: str):
    return redis_client.get(key)

async def delete_key(key: str):
    return redis_client.delete(key)

async def exists(key: str):
    return redis_client.exists(key)