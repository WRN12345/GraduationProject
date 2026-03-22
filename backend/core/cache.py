import redis.asyncio as redis
from core.config import settings

# 创建异步连接池（推荐用于高并发场景）
_pool = None


def get_redis_pool():
    """获取或创建异步 Redis 连接池"""
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,  # 最大连接数
        )
    return _pool


async def get_redis():
    """
    获取 Redis 异步连接
    
    使用方式：
    - FastAPI 依赖注入: redis: Redis = Depends(get_redis)
    - 异步生成器: redis = await get_redis().__anext__()
    
    注意：每次调用会自动从连接池获取连接，使用完毕后连接会返还给池
    """
    pool = get_redis_pool()
    r = redis.Redis(connection_pool=pool)
    try:
        yield r
    finally:
        await r.close()  # 关闭连接，将连接返还给连接池


async def close_redis_pool():
    """关闭 Redis 连接池（应用关闭时调用）"""
    global _pool
    if _pool:
        await _pool.disconnect()
        _pool = None
