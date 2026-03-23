"""
@Created on : 2026.3.13
@Author: wrn
@Des: Redis 缓存到 PostgreSQL 的定时同步任务
"""
import asyncio
import logging
from typing import List
from redis.asyncio import Redis
from tortoise.transactions import in_transaction

from core.database import db_retry
from core.config import settings
from models.vote import Vote
from models.post import Post
from models.comment import Comment
from models.bookmark import Bookmark
from core.services.content.vote_service import vote_service
from core.services.content.bookmark_service import bookmark_service

logger = logging.getLogger(__name__)


async def _get_redis() -> Redis:
    """从连接池获取 Redis 连接（不关闭，由连接池管理）"""
    from core.cache import get_redis_pool
    import redis.asyncio as aioredis
    pool = await get_redis_pool()
    return aioredis.Redis(connection_pool=pool)  # ✅ 复用连接池，不手动 close


async def sync_votes_to_db():
    """
    定时任务：同步 Redis 投票数据到 PostgreSQL
    频率：每 5 分钟执行一次
    """
    redis = await _get_redis()  # ✅ 不再用 __anext__()，不再 close()

    # 1. 同步帖子投票
    post_sync_key = vote_service._get_sync_key("post")
    post_ids = await redis.smembers(post_sync_key)

    if post_ids:
        logger.info(f"开始同步 {len(post_ids)} 个帖子的投票数据")
        try:
            await _sync_post_votes(redis, list(post_ids))
            await redis.delete(post_sync_key)
        except Exception as e:
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                logger.warning(f"数据库表不存在，跳过投票同步: {e}")
            else:
                raise

    # 2. 同步评论投票
    comment_sync_key = vote_service._get_sync_key("comment")
    comment_ids = await redis.smembers(comment_sync_key)

    if comment_ids:
        logger.info(f"开始同步 {len(comment_ids)} 个评论的投票数据")
        try:
            await _sync_comment_votes(redis, list(comment_ids))
            await redis.delete(comment_sync_key)
        except Exception as e:
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                logger.warning(f"数据库表不存在，跳过评论投票同步: {e}")
            else:
                raise


async def sync_bookmarks_to_db():
    """
    定时任务：同步 Redis 收藏数据到 PostgreSQL
    频率：每 5 分钟执行一次
    """
    redis = await _get_redis()  # ✅ 复用连接池

    sync_key = bookmark_service._get_sync_key()
    user_ids = await redis.smembers(sync_key)

    if not user_ids:
        return

    logger.info(f"开始同步 {len(user_ids)} 个用户的收藏数据")

    try:
        for user_id in user_ids:
            await _sync_user_bookmarks(redis, int(user_id))
        await redis.delete(sync_key)
        logger.info("收藏数据同步完成")
    except Exception as e:
        error_str = str(e).lower()
        if "relation" in error_str and "does not exist" in error_str:
            logger.warning(f"数据库表不存在，跳过收藏同步: {e}")
        else:
            raise


# ✅ 统一的带重连保护的循环工厂
async def _run_loop(task_name: str, task_fn, interval: int):
    """
    带重连保护的任务循环

    - Redis 连接异常：等 5 秒重试（不等完整 interval）
    - 其他异常：记录日志，等完整 interval 后继续
    """
    logger.info(f"{task_name} 启动")
    while True:
        try:
            await task_fn()
            await asyncio.sleep(interval)
        except (ConnectionError, OSError) as e:
            # Redis 连接断开，短暂等待后重试
            logger.warning(f"{task_name} Redis连接异常，5秒后重试: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"{task_name} 异常: {e}")
            await asyncio.sleep(interval)


async def start_sync_tasks():
    """启动同步任务，在应用启动时调用"""
    vote_interval = getattr(settings, 'VOTE_SYNC_INTERVAL', 300)
    bookmark_interval = getattr(settings, 'BOOKMARK_SYNC_INTERVAL', 300)

    logger.info("启动投票和收藏同步任务...")

    asyncio.create_task(
        _run_loop("投票同步", sync_votes_to_db, vote_interval)
    )
    asyncio.create_task(
        _run_loop("收藏同步", sync_bookmarks_to_db, bookmark_interval)
    )

    logger.info("同步任务启动完成")




async def _sync_post_votes(redis: Redis, post_ids: List[int]):
    """同步帖子投票到数据库"""
    for post_id in post_ids:
        post_id = int(post_id)

        # 从 Redis 获取计数
        upvotes, downvotes, score = await vote_service.get_vote_counts(
            redis, 'post', post_id
        )

        # 更新数据库
        await Post.filter(id=post_id).update(
            upvotes=upvotes,
            downvotes=downvotes,
            score=score
        )

        # 获取投票用户列表（可选，用于同步 Vote 记录）
        up_voters_key = vote_service._get_voters_key('post', post_id, 'up')
        down_voters_key = vote_service._get_voters_key('post', post_id, 'down')

        up_voter_ids = await redis.zrange(up_voters_key, 0, -1)
        down_voter_ids = await redis.zrange(down_voters_key, 0, -1)

        # 同步 Vote 记录（使用 upsert 逻辑）
        async with in_transaction():
            # 处理赞
            for user_id in up_voter_ids:
                user_id = int(user_id)
                vote = await Vote.get_or_none(
                    user_id=user_id,
                    post_id=post_id
                )

                if vote:
                    if vote.direction != 1:
                        vote.direction = 1
                        await vote.save()
                else:
                    await Vote.create(
                        user_id=user_id,
                        post_id=post_id,
                        direction=1
                    )

            # 处理踩
            for user_id in down_voter_ids:
                user_id = int(user_id)
                vote = await Vote.get_or_none(
                    user_id=user_id,
                    post_id=post_id
                )

                if vote:
                    if vote.direction != -1:
                        vote.direction = -1
                        await vote.save()
                else:
                    await Vote.create(
                        user_id=user_id,
                        post_id=post_id,
                        direction=-1
                    )

            # 删除不在 Redis 中的投票记录（取消投票的情况）
            all_voter_ids = set([int(uid) for uid in up_voter_ids + down_voter_ids])
            if all_voter_ids:
                await Vote.filter(
                    post_id=post_id,
                    user_id__not_in=all_voter_ids
                ).delete()


async def _sync_comment_votes(redis: Redis, comment_ids: List[int]):
    """同步评论投票到数据库"""
    for comment_id in comment_ids:
        comment_id = int(comment_id)

        # 从 Redis 获取计数
        upvotes, downvotes, score = await vote_service.get_vote_counts(
            redis, 'comment', comment_id
        )

        # 更新数据库
        await Comment.filter(id=comment_id).update(
            upvotes=upvotes,
            downvotes=downvotes,
            score=score
        )

        # 获取投票用户列表（可选，用于同步 Vote 记录）
        up_voters_key = vote_service._get_voters_key('comment', comment_id, 'up')
        down_voters_key = vote_service._get_voters_key('comment', comment_id, 'down')

        up_voter_ids = await redis.zrange(up_voters_key, 0, -1)
        down_voter_ids = await redis.zrange(down_voters_key, 0, -1)

        # 同步 Vote 记录（使用 upsert 逻辑）
        async with in_transaction():
            # 处理赞
            for user_id in up_voter_ids:
                user_id = int(user_id)
                vote = await Vote.get_or_none(
                    user_id=user_id,
                    comment_id=comment_id
                )

                if vote:
                    if vote.direction != 1:
                        vote.direction = 1
                        await vote.save()
                else:
                    await Vote.create(
                        user_id=user_id,
                        comment_id=comment_id,
                        direction=1
                    )

            # 处理踩
            for user_id in down_voter_ids:
                user_id = int(user_id)
                vote = await Vote.get_or_none(
                    user_id=user_id,
                    comment_id=comment_id
                )

                if vote:
                    if vote.direction != -1:
                        vote.direction = -1
                        await vote.save()
                else:
                    await Vote.create(
                        user_id=user_id,
                        comment_id=comment_id,
                        direction=-1
                    )

            # 删除不在 Redis 中的投票记录（取消投票的情况）
            all_voter_ids = set([int(uid) for uid in up_voter_ids + down_voter_ids])
            if all_voter_ids:
                await Vote.filter(
                    comment_id=comment_id,
                    user_id__not_in=all_voter_ids
                ).delete()


async def _sync_user_bookmarks(redis: Redis, user_id: int):
    """同步用户收藏到数据库"""
    from datetime import datetime, timezone

    bookmarks_key = bookmark_service._get_user_bookmarks_key(user_id)

    # 获取 Redis 中的所有收藏 post_ids 及时间戳
    bookmark_data = await redis.zrange(bookmarks_key, 0, -1, withscores=True)
    
    # 构建 post_id -> timestamp 映射
    post_timestamps = {int(pid): score for pid, score in bookmark_data}
    post_ids = list(post_timestamps.keys())

    # 获取数据库中现有的收藏
    existing_bookmarks = await Bookmark.filter(user_id=user_id).values_list('post_id', flat=True)
    existing_set = set(existing_bookmarks)
    redis_set = set(post_ids)

    # 找出需要添加的
    to_add = redis_set - existing_set

    # 找出需要删除的
    to_remove = existing_set - redis_set

    # 执行同步
    async with in_transaction():
        # 添加新收藏
        for post_id in to_add:
            try:
                # 从 Redis 时间戳转换 created_at
                timestamp = post_timestamps.get(post_id)
                if timestamp:
                    created_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                else:
                    created_at = datetime.now(timezone.utc)
                
                await Bookmark.create(
                    user_id=user_id,
                    post_id=post_id,
                    folder='default',
                    created_at=created_at
                )
            except Exception as e:
                logger.warning(f"添加收藏失败 user_id={user_id} post_id={post_id}: {e}")

        # 删除取消的收藏
        if to_remove:
            await Bookmark.filter(
                user_id=user_id,
                post_id__in=to_remove
            ).delete()

__all__ = [
    "sync_votes_to_db",
    "sync_bookmarks_to_db",
    "start_sync_tasks"
]
