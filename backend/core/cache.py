import redis.asyncio as redis
from backend.core.config import settings
from fastapi import Depends

# 创建连接池
pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    """Redis 依赖注入函数"""
    r = redis.Redis(connection_pool=pool)
    try:
        yield r
    finally:
        await r.close()


async def get_redis_direct():
    """获取 Redis 客户端"""
    """用于需要在函数内部直接使用 Redis 的场景"""
    return redis.Redis(connection_pool=pool)