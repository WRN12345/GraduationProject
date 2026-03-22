import asyncio
import redis.asyncio as redis
from core.config import settings

_pool: redis.ConnectionPool | None = None
_pool_lock = asyncio.Lock()


async def get_redis_pool() -> redis.ConnectionPool:
    """获取或创建异步 Redis 连接池（线程安全）"""
    global _pool
    if _pool is None:
        async with _pool_lock:
            if _pool is None:
                _pool = redis.ConnectionPool.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    max_connections=20,
                )
    return _pool


async def get_redis():
    """
    获取 Redis 异步连接

    使用方式：
    - FastAPI 依赖注入: redis: Redis = Depends(get_redis)

    注意：每次调用会自动从连接池获取连接，使用完毕后连接会返还给池
    """
    pool = await get_redis_pool()
    r = redis.Redis(connection_pool=pool)
    try:
        yield r
    finally:
        await r.aclose()


async def close_redis_pool():
    """关闭 Redis 连接池（应用关闭时调用）"""
    global _pool
    if _pool:
        await _pool.aclose()
        _pool = None