# import asyncio
# from backend.core.cache import get_redis
# from backend.models.post import Post

# async def sync_scores_to_db():
#     """
#     每隔一段时间，把 Redis 里的热度同步回 PostgreSQL
#     """
#     redis = await get_redis() 
#     pass