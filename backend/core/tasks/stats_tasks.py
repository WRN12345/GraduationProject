"""
@Created on : 2026.3.16
@Author: wrn
@Des: 统计数据同步任务 - 定期同步社区和用户统计数据到 Redis
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from core.database import db_retry
from core.cache import get_redis
from core.services.content.hot_content_service import hot_content_service
from core.services.infrastructure.redis_service import hot_rank_service
from models.community import Community
from models.user import User
from models.post import Post
from models.comment import Comment

logger = logging.getLogger(__name__)


@db_retry()
async def sync_community_stats():
    """
    定时任务：同步社区统计数据到 Redis

    频率：每 5 分钟执行一次

    更新内容：
    - 社区帖子数量
    - 社区最后活跃时间
    - 重新计算热度分数
    - 更新 Redis 排行榜
    """
    redis = await get_redis().__anext__()

    try:
        # 获取所有社区
        communities = await Community.all()

        if not communities:
            logger.info("没有找到社区，跳过统计同步")
            return

        logger.info(f"开始同步 {len(communities)} 个社区的统计数据")

        # 计算7天前的日期（用于统计近期活跃度）
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        for community in communities:
            try:
                # 计算帖子总数
                post_count = await Post.filter(
                    community_id=community.id,
                    deleted_at__isnull=True
                ).count()

                # 计算近7天帖子数
                recent_posts = await Post.filter(
                    community_id=community.id,
                    deleted_at__isnull=True,
                    created_at__gte=seven_days_ago
                ).count()

                # 更新数据库字段
                if hasattr(community, 'post_count'):
                    community.post_count = post_count
                # 如果有近期活动，更新最后活跃时间
                if recent_posts > 0 and hasattr(community, 'last_active_at'):
                    community.last_active_at = datetime.now(timezone.utc)
                await community.save()

                # 同步到 Redis
                await hot_rank_service.sync_community_rank_from_db(
                    redis=redis,
                    community_id=community.id,
                    member_count=community.member_count,
                    post_count=post_count,
                    recent_posts=recent_posts,
                    created_at=community.created_at
                )

            except Exception as e:
                logger.error(f"同步社区 {community.id} 统计数据失败: {e}")
                continue

        logger.info("社区统计数据同步完成")

    except Exception as e:
        logger.error(f"社区统计同步任务执行失败: {e}")
    finally:
        await redis.close()


@db_retry()
async def sync_user_stats():
    """
    定时任务：同步用户统计数据到 Redis

    频率：每 5 分钟执行一次

    更新内容：
    - 用户发帖数量
    - 用户评论数量
    - 用户最后活跃时间
    - 重新计算活跃度分数
    - 更新 Redis 排行榜
    """
    redis = await get_redis().__anext__()

    try:
        # 获取活跃用户（分批处理，避免内存问题）
        # 只同步最近活跃的用户（30天内有活动）
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        # 获取近期有发帖或评论的用户
        active_post_data = await Post.filter(
            deleted_at__isnull=True,
            created_at__gte=thirty_days_ago
        ).values('author_id')

        active_comment_data = await Comment.filter(
            deleted_at__isnull=True,
            created_at__gte=thirty_days_ago
        ).values('author_id')

        # 提取 author_id 并合并去重
        active_post_users = {item['author_id'] for item in active_post_data}
        active_comment_users = {item['author_id'] for item in active_comment_data}
        active_user_ids = active_post_users | active_comment_users

        if not active_user_ids:
            logger.info("没有找到活跃用户，跳过统计同步")
            return

        logger.info(f"开始同步 {len(active_user_ids)} 个活跃用户的统计数据")

        # 计算7天前的日期（用于统计近期活跃度）
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        for user_id in active_user_ids:
            try:
                user = await User.get_or_none(id=user_id)
                if not user or not user.is_active:
                    continue

                # 计算帖子总数
                post_count = await Post.filter(
                    author_id=user_id,
                    deleted_at__isnull=True
                ).count()

                # 计算评论总数
                comment_count = await Comment.filter(
                    author_id=user_id,
                    deleted_at__isnull=True
                ).count()

                # 计算近7天活跃度（发帖+评论）
                recent_posts = await Post.filter(
                    author_id=user_id,
                    deleted_at__isnull=True,
                    created_at__gte=seven_days_ago
                ).count()

                recent_comments = await Comment.filter(
                    author_id=user_id,
                    deleted_at__isnull=True,
                    created_at__gte=seven_days_ago
                ).count()

                recent_activity = recent_posts + recent_comments

                # 更新数据库字段（检查字段是否存在）
                if hasattr(user, 'post_count'):
                    user.post_count = post_count
                if hasattr(user, 'comment_count'):
                    user.comment_count = comment_count
                # 如果有近期活动，更新最后活跃时间
                if recent_activity > 0 and hasattr(user, 'last_active_at'):
                    user.last_active_at = datetime.now(timezone.utc)
                await user.save()

                # 同步到 Redis
                await hot_rank_service.sync_user_rank_from_db(
                    redis=redis,
                    user_id=user_id,
                    karma=user.karma,
                    post_count=post_count,
                    comment_count=comment_count,
                    recent_activity=recent_activity,
                    last_login=user.last_login,
                    created_at=user.created_at
                )

            except Exception as e:
                logger.error(f"同步用户 {user_id} 统计数据失败: {e}")
                continue

        logger.info("活跃用户统计数据同步完成")

    except Exception as e:
        logger.error(f"用户统计同步任务执行失败: {e}")
    finally:
        await redis.close()


async def start_stats_tasks():
    """
    启动统计同步任务

    在应用启动时调用，启动两个定时任务：
    1. sync_community_stats - 每5分钟执行
    2. sync_user_stats - 每5分钟执行
    """
    stats_sync_interval = 300  # 5分钟

    async def community_stats_loop():
        """社区统计同步循环"""
        while True:
            try:
                await sync_community_stats()
            except Exception as e:
                logger.error(f"社区统计同步循环异常: {e}")
            await asyncio.sleep(stats_sync_interval)

    async def user_stats_loop():
        """用户统计同步循环"""
        while True:
            try:
                await sync_user_stats()
            except Exception as e:
                logger.error(f"用户统计同步循环异常: {e}")
            await asyncio.sleep(stats_sync_interval)

    # 启动任务
    logger.info("启动统计同步任务...")
    asyncio.create_task(community_stats_loop())
    asyncio.create_task(user_stats_loop())
    logger.info("统计同步任务启动完成")


__all__ = [
    "sync_community_stats",
    "sync_user_stats",
    "start_stats_tasks"
]
