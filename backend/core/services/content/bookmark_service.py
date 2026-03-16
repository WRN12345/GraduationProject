"""
@Created on : 2026.3.13
@Author: wrn
@Des: 收藏服务 - Redis 缓存 + 异步落库
"""
from typing import List, Optional
from datetime import datetime, timezone
from redis.asyncio import Redis
from models.user import User
from models.post import Post
from models.bookmark import Bookmark
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class BookmarkService:
    """收藏服务 - Redis + 异步落库"""

    # Redis Key 前缀
    USER_BOOKMARKS_PREFIX = "user:bookmarks"
    POST_BOOKMARK_COUNTS_PREFIX = "post:bookmark_counts"
    BOOKMARK_DETAILS_PREFIX = "user:bookmark_details"
    SYNC_PREFIX = "bookmark:sync"

    @staticmethod
    def _get_user_bookmarks_key(user_id: int) -> str:
        """获取用户收藏列表 key"""
        return f"{BookmarkService.USER_BOOKMARKS_PREFIX}:{user_id}"

    @staticmethod
    def _get_post_count_key(post_id: int) -> str:
        """获取帖子收藏计数 key"""
        return f"{BookmarkService.POST_BOOKMARK_COUNTS_PREFIX}:{post_id}"

    @staticmethod
    def _get_details_key(user_id: int, post_id: int) -> str:
        """获取收藏详情 key"""
        return f"{BookmarkService.BOOKMARK_DETAILS_PREFIX}:{user_id}:{post_id}"

    @staticmethod
    def _get_sync_key() -> str:
        """获取同步标记 key"""
        return f"{BookmarkService.SYNC_PREFIX}:users"

    async def is_bookmarked(
        self,
        redis: Redis,
        user_id: int,
        post_id: int
    ) -> bool:
        """检查是否已收藏"""
        key = self._get_user_bookmarks_key(user_id)
        score = await redis.zscore(key, str(post_id))  # 统一使用字符串
        return score is not None

    async def get_bookmark_count(
        self,
        redis: Redis,
        post_id: int
    ) -> int:
        """获取帖子收藏数"""
        key = self._get_post_count_key(post_id)
        count = await redis.get(key)
        return max(0, int(count)) if count else 0

    async def add_bookmark(
        self,
        redis: Redis,
        user: User,
        post: Post,
        folder: Optional[str] = None,
        note: Optional[str] = None
    ) -> dict:
        """
        添加收藏
        """
        # 1. 检查是否已收藏
        if await self.is_bookmarked(redis, user.id, post.id):
            return {"error": "已经收藏过了"}

        # 2. 获取 TTL 配置
        count_ttl = getattr(settings, 'REDIS_BOOKMARK_COUNT_TTL', 3600)
        details_ttl = getattr(settings, 'REDIS_BOOKMARK_DETAILS_TTL', 86400)

        # 3. 更新 Redis
        pipe = redis.pipeline()
        timestamp = datetime.now(timezone.utc).timestamp()

        # 3.1 添加到用户收藏列表
        bookmarks_key = self._get_user_bookmarks_key(user.id)
        pipe.zadd(bookmarks_key, {str(post.id): timestamp})

        # 3.2 增加帖子收藏计数
        count_key = self._get_post_count_key(post.id)
        pipe.incr(count_key)
        pipe.expire(count_key, count_ttl)

        # 3.3 缓存收藏详情
        details_key = self._get_details_key(user.id, post.id)

        # 安全获取时间戳（带时区错误处理）
        try:
            bookmarked_at = datetime.now(timezone.utc).isoformat()
        except Exception as e:
            logger.warning(f"时区处理失败，使用系统时间: {e}")
            bookmarked_at = datetime.now().isoformat()

        details = {
            'post_id': str(post.id),
            'title': post.title,
            'author': post.author.username if post.author and hasattr(post.author, 'username') else str(user.id),
            'created_at': post.created_at.isoformat(),
            'bookmarked_at': bookmarked_at
        }
        pipe.hset(details_key, mapping=details)
        pipe.expire(details_key, details_ttl)

        await pipe.execute()

        # 4. 标记需要同步到数据库
        sync_key = self._get_sync_key()
        await redis.sadd(sync_key, user.id)
        await redis.expire(sync_key, 3600)

        return {
            "success": True,
            "message": "收藏成功"
        }

    async def remove_bookmark(
        self,
        redis: Redis,
        user: User,
        post_id: int
    ) -> dict:
        """
        取消收藏
        """
        # 1. 检查是否已收藏
        if not await self.is_bookmarked(redis, user.id, post_id):
            return {"error": "未收藏该帖子"}

        # 2. 更新 Redis
        pipe = redis.pipeline()

        # 2.1 从用户收藏列表移除
        bookmarks_key = self._get_user_bookmarks_key(user.id)
        pipe.zrem(bookmarks_key, str(post_id))

        # 2.2 减少帖子收藏计数（先检查是否大于0，防止负数）
        count_key = self._get_post_count_key(post_id)
        current_count = await redis.get(count_key)
        if current_count and int(current_count) > 0:
            pipe.decr(count_key)

        # 2.3 删除收藏详情缓存
        details_key = self._get_details_key(user.id, post_id)
        pipe.delete(details_key)

        await pipe.execute()

        # 3. 标记需要同步到数据库
        sync_key = self._get_sync_key()
        await redis.sadd(sync_key, user.id)
        await redis.expire(sync_key, 3600)

        return {
            "success": True,
            "message": "已取消收藏"
        }

    async def get_user_bookmarks(
        self,
        redis: Redis,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        获取用户收藏列表
        """
        # 1. 从 Redis ZSET 获取收藏的 post_ids（倒序）
        bookmarks_key = self._get_user_bookmarks_key(user_id)
        total = await redis.zcard(bookmarks_key)

        post_ids = await redis.zrevrange(
            bookmarks_key,
            start=skip,
            end=skip + limit - 1
        )

        if not post_ids:
            return {
                "items": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "has_more": False
            }

        post_ids = [int(pid) for pid in post_ids]

        # 2. 批量获取缓存详情
        cached_details = {}
        pipe = redis.pipeline()
        for post_id in post_ids:
            details_key = self._get_details_key(user_id, post_id)
            pipe.hgetall(details_key)

        results = await pipe.execute()

        for post_id, data in zip(post_ids, results):
            if data:
                cached_details[post_id] = data

        # 3. 找出缓存未命中的
        missing_ids = [pid for pid in post_ids if pid not in cached_details]

        # 4. 从数据库获取
        if missing_ids:
            db_posts = await Post.filter(
                id__in=missing_ids,
                deleted_at__isnull=True
            ).select_related('author', 'community').prefetch_related('attachments')

            for post in db_posts:
                # 获取收藏时间
                bookmark = await Bookmark.filter(
                    user_id=user_id,
                    post_id=post.id
                ).first()

                cached_details[post.id] = {
                    'post_id': post.id,
                    'title': post.title,
                    'author': post.author.username if post.author else '',
                    'created_at': post.created_at.isoformat(),
                    'bookmarked_at': bookmark.created_at.isoformat() if bookmark else ''
                }

                # 回填缓存
                details_ttl = getattr(settings, 'REDIS_BOOKMARK_DETAILS_TTL', 86400)
                details_key = self._get_details_key(user_id, post.id)
                await redis.hset(details_key, mapping=cached_details[post.id])
                await redis.expire(details_key, details_ttl)

        # 5. 按 post_ids 顺序排序
        items = [cached_details.get(pid, {}) for pid in post_ids if pid in cached_details]

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }

    async def get_user_bookmarked_posts(
        self,
        redis: Redis,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        current_user: Optional[User] = None
    ) -> dict:
        """
        获取用户收藏的帖子列表（完整 PostOut 格式）

        Args:
            redis: Redis 客户端
            user_id: 用户 ID
            skip: 跳过条数
            limit: 返回条数
            current_user: 当前用户（用于添加用户状态）

        Returns:
            dict: 分页帖子列表（PostOut 格式）
        """
        # 延迟导入避免循环依赖
        from core.services.content.vote_service import vote_service
        from core.services.content.post_service import post_service

        # 1. 从 Redis ZSET 获取收藏的 post_ids（倒序，按收藏时间）
        bookmarks_key = self._get_user_bookmarks_key(user_id)
        total = await redis.zcard(bookmarks_key)

        if total == 0:
            return {
                "items": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "has_more": False
            }

        post_ids = await redis.zrevrange(
            bookmarks_key,
            start=skip,
            end=skip + limit - 1
        )

        if not post_ids:
            return {
                "items": [],
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": False
            }

        post_ids = [int(pid) for pid in post_ids]

        # 2. 从数据库获取完整的帖子信息
        posts = await Post.filter(
            id__in=post_ids,
            deleted_at__isnull=True
        ).select_related('author', 'community').prefetch_related('attachments')

        # 3. 按 Redis 中的顺序重新排序（保持收藏时间倒序）
        post_dict = {post.id: post for post in posts}
        sorted_posts = [post_dict[pid] for pid in post_ids if pid in post_dict]

        # 4. 构建响应数据（使用 post_service 的 _build_post_dict 方法）
        items = []
        for post in sorted_posts:
            post_dict_data = post_service._build_post_dict(post)

            # 添加投票数据
            upvotes, downvotes, score = await vote_service.get_vote_counts(
                redis, 'post', post.id
            )
            post_dict_data["upvotes"] = upvotes
            post_dict_data["downvotes"] = downvotes
            post_dict_data["score"] = score

            # 添加用户状态字段
            if current_user:
                user_state = await post_service._get_user_state(
                    redis, post.id, current_user
                )
                post_dict_data.update(user_state)
            else:
                post_dict_data["user_vote"] = 0
                post_dict_data["bookmarked"] = True  # 列表中的都是已收藏的
                post_dict_data["bookmark_count"] = await self.get_bookmark_count(redis, post.id)

            items.append(post_dict_data)

        # 5. 计算是否有更多数据
        has_more = skip + limit < total

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more
        }

    async def batch_check_bookmarked(
        self,
        redis: Redis,
        user_id: int,
        post_ids: List[int]
    ) -> dict:
        """
        批量检查收藏状态

        Returns:
            {post_id: bool}
        """
        if not post_ids:
            return {}

        key = self._get_user_bookmarks_key(user_id)
        pipe = redis.pipeline()

        for post_id in post_ids:
            pipe.zscore(key, str(post_id))  # 统一使用字符串

        results = await pipe.execute()

        bookmarked = {}
        for post_id, score in zip(post_ids, results):
            bookmarked[post_id] = score is not None

        return bookmarked

    async def batch_get_bookmark_counts(
        self,
        redis: Redis,
        post_ids: List[int]
    ) -> dict:
        """
        批量获取多个帖子的收藏数

        Returns:
            {post_id: int}
        """
        if not post_ids:
            return {}

        results = {}
        pipe = redis.pipeline()

        for post_id in post_ids:
            key = self._get_post_count_key(post_id)
            pipe.get(key)

        counts = await pipe.execute()

        for post_id, count in zip(post_ids, counts):
            results[post_id] = int(count) if count else 0

        return results


# 导出服务实例
bookmark_service = BookmarkService()


__all__ = ["BookmarkService", "bookmark_service"]
