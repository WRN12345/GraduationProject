"""
@Created on : 2025/12/8
@Author: wrn
@Des: Redis 与 PostgreSQL 数据同步任务
"""
import asyncio
import logging
from typing import Optional
logger = logging.getLogger(__name__)
from core.cache import get_redis
from core.services.infrastructure.redis_service import hot_rank_service
from models.post import Post
from core.config import settings
from core.database import db_retry, check_db_connection, ensure_connection


async def sync_post_stats_to_db():
    """
    定时任务：将 Redis 交互计数同步到 PostgreSQL

    频率：每分钟执行一次
    同步内容：
    - upvotes/downvotes 计数
    - 重新计算并更新 hot_rank
    """
    from tortoise.exceptions import OperationalError as TortoiseOperationalError

    redis = await get_redis().__anext__()

    try:
        # 获取所有有交互的帖子 key
        pattern = "post:interactions:*"
        keys = []
        async for key in redis.scan_iter(match=pattern):
            keys.append(key)

        if not keys:
            return

        logger.info(f"开始同步 {len(keys)} 个帖子的交互数据到 PostgreSQL")

        # 批量获取交互数据
        pipe = redis.pipeline()
        for key in keys:
            pipe.hgetall(key)
        interactions_list = await pipe.execute()

        # 同步到数据库
        synced_count = 0
        for key, interactions in zip(keys, interactions_list):
            if not interactions:
                continue

            # 提取 post_id
            post_id = int(key.split(":")[-1])

            # 使用重试机制同步单个帖子
            try:
                success = await _sync_single_post_with_retry(
                    redis=redis,
                    post_id=post_id,
                    interactions=interactions
                )
                if success:
                    synced_count += 1
            except Exception as e:
                error_str = str(e).lower()
                if "relation" in error_str and "does not exist" in error_str:
                    # 表不存在，跳过本次同步（可能是迁移未运行）
                    logger.warning(f"数据库表不存在，跳过帖子 {post_id} 的同步: {e}")
                    break  # 跳出循环，因为后续的帖子也会失败
                else:
                    logger.error(f"同步帖子 {post_id} 最终失败（已重试）: {e}")

        logger.info(f"成功同步 {synced_count} 个帖子到 PostgreSQL")

    finally:
        await redis.close()


@db_retry()
async def _sync_single_post_with_retry(redis, post_id: int, interactions: dict) -> bool:
    """
    同步单个帖子的数据到数据库（带重试）

    Args:
        redis: Redis 连接
        post_id: 帖子 ID
        interactions: 交互数据

    Returns:
        bool: 是否成功同步
    """
    post = await Post.get_or_none(id=post_id)
    if not post:
        # 帖子不存在，清理 Redis 数据（不重试）
        await redis.delete(f"post:interactions:{post_id}")
        return False

    # 解析交互数据
    upvote_count = int(interactions.get('upvote_count', 0))
    downvote_count = int(interactions.get('downvote_count', 0))

    vote_weight = getattr(settings, 'HOT_VOTE_WEIGHT', 10)
    upvotes = upvote_count // vote_weight
    downvotes = downvote_count // vote_weight

    # 更新数据库（这里会自动重试如果连接失败）
    await Post.filter(id=post_id).update(
        upvotes=upvotes,
        downvotes=downvotes,
        score=upvotes - downvotes
    )

    # 重新计算热度
    await post.update_hot_rank()

    return True


async def update_hot_ranks():
    """
    定时任务：批量重新计算并更新热门帖子热度

    用于处理以下场景：
    - 帖子创建后初始化热度
    - 时间衰减导致热度变化
    - 数据修正后重新计算

    注意：不使用 @db_retry 装饰器，因为表不存在时重试没有意义
    """
    redis = await get_redis().__anext__()

    try:
        # 获取所有帖子（只取最近的，避免全表扫描）
        posts = await Post.filter(
            deleted_at__isnull=True
        ).limit(1000).order_by("-created_at")

        logger.info(f"开始更新 {len(posts)} 个帖子的热度")

        for post in posts:
            try:
                # 从数据库同步到 Redis
                await hot_rank_service.sync_post_rank_from_db(
                    redis=redis,
                    post_id=post.id,
                    upvotes=post.upvotes,
                    downvotes=post.downvotes,
                    created_at=post.created_at,
                    community_id=post.community_id
                )
            except Exception as e:
                error_str = str(e).lower()
                if "relation" in error_str and "does not exist" in error_str:
                    logger.warning(f"数据库表不存在，跳过热度更新: {e}")
                    break
                else:
                    logger.error(f"更新帖子 {post.id} 热度失败: {e}")

        logger.info("热度更新完成")

    except Exception as e:
        logger.error(f"热度更新任务执行失败: {e}")
    finally:
        await redis.close()


async def start_background_tasks():
    """
    启动后台定时任务

    在应用启动时调用，启动两个定时任务：
    1. sync_post_stats_to_db - 每分钟执行
    2. update_hot_ranks - 每5分钟执行
    """
    sync_interval = getattr(settings, 'REDIS_SYNC_INTERVAL', 60)

    async def sync_loop():
        """同步循环"""
        while True:
            try:
                # 执行前检查连接
                if not await check_db_connection():
                    logger.warning("数据库连接不可用，尝试重新连接...")
                    await ensure_connection()

                await sync_post_stats_to_db()
            except Exception as e:
                logger.error(f"同步循环异常: {e}")
            await asyncio.sleep(sync_interval)

    async def hot_rank_loop():
        """热度更新循环"""
        while True:
            try:
                # 执行前检查连接
                if not await check_db_connection():
                    logger.warning("数据库连接不可用，尝试重新连接...")
                    await ensure_connection()

                await update_hot_ranks()
            except Exception as e:
                logger.error(f"热度更新循环异常: {e}")
            await asyncio.sleep(300)  # 5分钟

    # 启动两个任务
    logger.info("启动 Redis 同步后台任务...")
    asyncio.create_task(sync_loop())
    asyncio.create_task(hot_rank_loop())
    logger.info("后台任务启动完成")


# 保留旧的接口（兼容性）
async def sync_scores_to_db():
    """
    @Deprecated: 使用 sync_post_stats_to_db 替代
    """
    await sync_post_stats_to_db()


__all__ = [
    "sync_post_stats_to_db",
    "update_hot_ranks",
    "start_background_tasks",
    "sync_scores_to_db",
]
