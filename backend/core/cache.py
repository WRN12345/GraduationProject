import redis.asyncio as redis 
from backend.core.config import settings

# 创建连接池
pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    r = redis.Redis(connection_pool=pool)
    try:
        yield r
    finally:
        await r.close()