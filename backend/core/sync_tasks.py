"""
@Created on : 2026.3.13
@Author: wrn
@Des: Redis 缓存到 PostgreSQL 的定时同步任务
"""
import asyncio
import logging
from typing import List
from datetime import datetime
from redis.asyncio import Redis
from tortoise.transactions import in_transaction

from core.database import db_retry
from core.config import settings
from models.vote import Vote
from models.post import Post
from models.comment import Comment
from models.bookmark import Bookmark
from core.vote_service import vote_service
from core.bookmark_service import bookmark_service

logger = logging.getLogger(__name__)


@db_retry()
async def sync_votes_to_db():
    """
    定时任务：同步 Redis 投票数据到 PostgreSQL

    频率：每 5 分钟执行一次
    """
    from core.cache import get_redis

    redis: Redis = await get_redis().__anext__()

    try:
        # 1. 获取需要同步的帖子 ID
        post_sync_key = vote_service._get_sync_key("post")
        post_ids = await redis.smembers(post_sync_key)

        if post_ids:
            logger.info(f"开始同步 {len(post_ids)} 个帖子的投票数据")
            await _sync_post_votes(redis, list(post_ids))
            await redis.delete(post_sync_key)

        # 2. 获取需要同步的评论 ID
        comment_sync_key = vote_service._get_sync_key("comment")
        comment_ids = await redis.smembers(comment_sync_key)

        if comment_ids:
            logger.info(f"开始同步 {len(comment_ids)} 个评论的投票数据")
            await _sync_comment_votes(redis, list(comment_ids))
            await redis.delete(comment_sync_key)

    finally:
        await redis.close()


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


@db_retry()
async def sync_bookmarks_to_db():
    """
    定时任务：同步 Redis 收藏数据到 PostgreSQL

    频率：每 5 分钟执行一次
    """
    from core.cache import get_redis

    redis: Redis = await get_redis().__anext__()

    try:
        # 获取需要同步的用户 ID
        sync_key = bookmark_service._get_sync_key()
        user_ids = await redis.smembers(sync_key)

        if not user_ids:
            return

        logger.info(f"开始同步 {len(user_ids)} 个用户的收藏数据")

        for user_id in user_ids:
            user_id = int(user_id)
            await _sync_user_bookmarks(redis, user_id)

        await redis.delete(sync_key)
        logger.info("收藏数据同步完成")

    finally:
        await redis.close()


async def _sync_user_bookmarks(redis: Redis, user_id: int):
    """同步用户收藏到数据库"""
    bookmarks_key = bookmark_service._get_user_bookmarks_key(user_id)

    # 获取 Redis 中的所有收藏 post_ids
    post_ids = await redis.zrange(bookmarks_key, 0, -1)
    post_ids = [int(pid) for pid in post_ids]

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
                await Bookmark.create(
                    user_id=user_id,
                    post_id=post_id,
                    folder='default',
                    created_at=datetime.now()  # 显式传递 naive datetime，避免时区错误
                )
            except Exception as e:
                logger.warning(f"添加收藏失败 user_id={user_id} post_id={post_id}: {e}")

        # 删除取消的收藏
        if to_remove:
            await Bookmark.filter(
                user_id=user_id,
                post_id__in=to_remove
            ).delete()


async def start_sync_tasks():
    """
    启动同步任务

    在应用启动时调用
    """
    # 获取同步间隔配置
    vote_sync_interval = getattr(settings, 'VOTE_SYNC_INTERVAL', 300)  # 默认 5 分钟
    bookmark_sync_interval = getattr(settings, 'BOOKMARK_SYNC_INTERVAL', 300)  # 默认 5 分钟

    async def vote_sync_loop():
        """投票同步循环"""
        while True:
            try:
                await sync_votes_to_db()
            except Exception as e:
                logger.error(f"投票同步异常: {e}")
            await asyncio.sleep(vote_sync_interval)

    async def bookmark_sync_loop():
        """收藏同步循环"""
        while True:
            try:
                await sync_bookmarks_to_db()
            except Exception as e:
                logger.error(f"收藏同步异常: {e}")
            await asyncio.sleep(bookmark_sync_interval)

    # 启动任务
    logger.info("启动投票和收藏同步任务...")
    asyncio.create_task(vote_sync_loop())
    asyncio.create_task(bookmark_sync_loop())
    logger.info("同步任务启动完成")


__all__ = [
    "sync_votes_to_db",
    "sync_bookmarks_to_db",
    "start_sync_tasks"
]
