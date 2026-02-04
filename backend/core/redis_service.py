"""
@Created on : 2026.2.3
@Author: wrn
@Des: Redis 热度排行和缓存服务
"""
import json
import math
from typing import Optional, List
from datetime import datetime, timezone
from redis.asyncio import Redis
from backend.core.config import settings


class HotRankService:
    """热度排行服务 - 使用 Redis ZSET 管理热门帖子"""

    # Redis Key 前缀
    HOT_POSTS_GLOBAL = "hot:posts:global"
    HOT_POSTS_COMMUNITY = "hot:posts:community"
    POST_INTERACTIONS = "post:interactions"  # Hash 存储交互计数

    @staticmethod
    def _get_post_interaction_key(post_id: int) -> str:
        """获取帖子交互计数 key"""
        return f"{HotRankService.POST_INTERACTIONS}:{post_id}"

    @staticmethod
    def _get_hot_posts_key(community_id: Optional[int] = None) -> str:
        """获取热门帖子 ZSET key"""
        if community_id:
            return f"{HotRankService.HOT_POSTS_COMMUNITY}:{community_id}"
        return HotRankService.HOT_POSTS_GLOBAL

    @staticmethod
    def _calculate_hot_rank(
        upvotes: int,
        downvotes: int,
        created_at: datetime,
        view_count: int = 0,
        share_count: int = 0
    ) -> float:
        """
        计算 Reddit 风格的热度分数

        公式: log10(|score|) + (timestamp / 45000)
        加入浏览和分享权重
        """
        # 基础分数（投票）
        vote_score = upvotes - downvotes
        if vote_score == 0:
            base_score = 0
        else:
            base_score = math.log10(max(abs(vote_score), 1))

        # 交互权重（浏览和分享）
        interaction_score = (
            view_count * getattr(settings, 'HOT_VIEW_WEIGHT', 1) +
            share_count * getattr(settings, 'HOT_SHARE_WEIGHT', 5)
        )

        # 时间组件（Unix 时间戳秒数）
        epoch_seconds = int(created_at.timestamp())

        # 热度分数 = 基础分数 + 时间衰减 + 交互加权
        hot_score = base_score + (epoch_seconds / 45000) + (interaction_score * 0.001)

        return round(hot_score, 7)

    async def increment_interaction(
        self,
        redis: Redis,
        post_id: int,
        interaction_type: str,
        created_at: Optional[datetime] = None
    ) -> float:
        """
        增加用户交互并更新热度

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            interaction_type: 交互类型 ('view', 'share', 'upvote', 'downvote')
            created_at: 帖子创建时间（用于计算热度）

        Returns:
            新的热度分数
        """
        key = self._get_post_interaction_key(post_id)

        # 获取权重配置
        weights = {
            'view': getattr(settings, 'HOT_VIEW_WEIGHT', 1),
            'share': getattr(settings, 'HOT_SHARE_WEIGHT', 5),
            'upvote': getattr(settings, 'HOT_VOTE_WEIGHT', 10),
            'downvote': getattr(settings, 'HOT_VOTE_WEIGHT', 10),
        }

        weight = weights.get(interaction_type, 1)

        # 原子更新交互计数
        field = f"{interaction_type}_count"
        await redis.hincrby(key, field, weight)

        # 获取当前所有交互数据
        interactions = await redis.hgetall(key)

        # 计算热度（需要帖子创建时间）
        if created_at:
            upvotes = int(interactions.get('upvote_count', 0)) // getattr(settings, 'HOT_VOTE_WEIGHT', 10)
            downvotes = int(interactions.get('downvote_count', 0)) // getattr(settings, 'HOT_VOTE_WEIGHT', 10)
            view_count = int(interactions.get('view_count', 0))
            share_count = int(interactions.get('share_count', 0))

            hot_rank = self._calculate_hot_rank(
                upvotes=upvotes,
                downvotes=downvotes,
                created_at=created_at,
                view_count=view_count,
                share_count=share_count
            )

            # 更新到全局热门 ZSET
            await redis.zadd(self.HOT_POSTS_GLOBAL, {str(post_id): hot_rank})

            return hot_rank

        return 0.0

    async def sync_post_rank_from_db(
        self,
        redis: Redis,
        post_id: int,
        upvotes: int,
        downvotes: int,
        created_at: datetime,
        community_id: Optional[int] = None
    ):
        """
        从数据库同步帖子热度到 Redis

        用于初始化或定时同步
        """
        hot_rank = self._calculate_hot_rank(
            upvotes=upvotes,
            downvotes=downvotes,
            created_at=created_at
        )

        # 更新全局热门
        await redis.zadd(self.HOT_POSTS_GLOBAL, {str(post_id): hot_rank})

        # 更新社区热门
        if community_id:
            community_key = self._get_hot_posts_key(community_id)
            await redis.zadd(community_key, {str(post_id): hot_rank})

    async def get_hot_post_ids(
        self,
        redis: Redis,
        limit: int = 20,
        offset: int = 0,
        community_id: Optional[int] = None
    ) -> List[int]:
        """
        获取热门帖子 ID 列表

        Args:
            redis: Redis 客户端
            limit: 返回数量
            offset: 偏移量
            community_id: 社区 ID（可选，为空则返回全局热门）

        Returns:
            帖子 ID 列表（按热度降序）
        """
        key = self._get_hot_posts_key(community_id)

        # ZREVRANGE 返回有序集合中指定范围的成员（分数从高到低）
        post_ids = await redis.zrevrange(
            key,
            start=offset,
            end=offset + limit - 1,
        )

        return [int(pid) for pid in post_ids]

    async def remove_post(self, redis: Redis, post_id: int, community_id: Optional[int] = None):
        """从热门榜中移除帖子（软删除时调用）"""
        await redis.zrem(self.HOT_POSTS_GLOBAL, str(post_id))

        if community_id:
            community_key = self._get_hot_posts_key(community_id)
            await redis.zrem(community_key, str(post_id))

        # 清理交互计数
        await redis.delete(self._get_post_interaction_key(post_id))


class PostCacheService:
    """帖子详情缓存服务"""

    POST_DETAIL_PREFIX = "post:detail"
    POST_LIST_PREFIX = "post:list"
    DEFAULT_TTL = getattr(settings, 'REDIS_POST_DETAIL_TTL', 600)  # 默认 10 分钟
    LIST_TTL = getattr(settings, 'REDIS_POST_LIST_TTL', 300)  # 列表缓存 5 分钟

    @staticmethod
    def _get_post_detail_key(post_id: int) -> str:
        """获取帖子详情缓存 key"""
        return f"{PostCacheService.POST_DETAIL_PREFIX}:{post_id}"

    @staticmethod
    def _get_post_list_key(post_id: int) -> str:
        """获取帖子列表缓存 key"""
        return f"{PostCacheService.POST_LIST_PREFIX}:{post_id}"

    @staticmethod
    def _get_post_detail_key(post_id: int) -> str:
        """获取帖子详情缓存 key"""
        return f"{PostCacheService.POST_DETAIL_PREFIX}:{post_id}"

    async def cache_post(
        self,
        redis: Redis,
        post_id: int,
        post_data: dict,
        ttl: Optional[int] = None
    ):
        """
        缓存帖子详情

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            post_data: 帖子数据字典
            ttl: 过期时间（秒），默认使用配置值
        """
        key = self._get_post_detail_key(post_id)
        await redis.setex(
            key,
            ttl or self.DEFAULT_TTL,
            json.dumps(post_data, default=str)
        )

    async def cache_posts_batch(
        self,
        redis: Redis,
        posts: List[dict],
        ttl: Optional[int] = None
    ):
        """
        批量缓存帖子详情

        Args:
            redis: Redis 客户端
            posts: 帖子数据列表
            ttl: 过期时间（秒）
        """
        pipe = redis.pipeline()
        for post in posts:
            key = self._get_post_detail_key(post['id'])
            pipe.setex(
                key,
                ttl or self.DEFAULT_TTL,
                json.dumps(post, default=str)
            )
        await pipe.execute()

    async def get_cached_post(
        self,
        redis: Redis,
        post_id: int
    ) -> Optional[dict]:
        """
        获取缓存的帖子详情

        Returns:
            帖子数据字典，未命中返回 None
        """
        key = self._get_post_detail_key(post_id)
        data = await redis.get(key)

        if data:
            return json.loads(data)
        return None

    async def get_cached_posts_batch(
        self,
        redis: Redis,
        post_ids: List[int]
    ) -> dict:
        """
        批量获取缓存的帖子详情

        Returns:
            dict: {post_id: post_data} 未命中的不在结果中
        """
        if not post_ids:
            return {}

        keys = [self._get_post_detail_key(pid) for pid in post_ids]
        values = await redis.mget(keys)

        result = {}
        for pid, value in zip(post_ids, values):
            if value:
                result[pid] = json.loads(value)

        return result

    # --- 列表缓存方法 ---

    async def cache_post_list(
        self,
        redis: Redis,
        post_id: int,
        list_data: dict,
        ttl: Optional[int] = None
    ):
        """
        缓存帖子列表信息（不含完整内容）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            list_data: 列表数据 (id, title, author, score, created_at)
            ttl: 过期时间（秒）
        """
        key = self._get_post_list_key(post_id)
        await redis.setex(
            key,
            ttl or self.LIST_TTL,
            json.dumps(list_data, default=str)
        )

    async def get_cached_post_list(
        self,
        redis: Redis,
        post_id: int
    ) -> Optional[dict]:
        """
        获取缓存的列表信息

        Returns:
            列表数据字典，未命中返回 None
        """
        key = self._get_post_list_key(post_id)
        data = await redis.get(key)

        if data:
            return json.loads(data)
        return None

    async def cache_posts_list_batch(
        self,
        redis: Redis,
        posts: List[dict],
        ttl: Optional[int] = None
    ):
        """
        批量缓存列表信息

        Args:
            redis: Redis 客户端
            posts: 帖子数据列表
            ttl: 过期时间（秒）
        """
        pipe = redis.pipeline()
        for post in posts:
            key = self._get_post_list_key(post['id'])
            # 只缓存列表所需字段
            list_data = {
                "id": post['id'],
                "title": post['title'],
                "score": post['score'],
                "hot_rank": post.get('hot_rank', 0),
                "author_id": post['author_id'],
                "author": post.get('author'),
                "community_id": post.get('community_id'),
                "community": post.get('community'),
                "created_at": post['created_at'],
            }
            pipe.setex(
                key,
                ttl or self.LIST_TTL,
                json.dumps(list_data, default=str)
            )
        await pipe.execute()

    async def get_cached_posts_list_batch(
        self,
        redis: Redis,
        post_ids: List[int]
    ) -> dict:
        """
        批量获取列表缓存

        Returns:
            dict: {post_id: list_data} 未命中的不在结果中
        """
        if not post_ids:
            return {}

        keys = [self._get_post_list_key(pid) for pid in post_ids]
        values = await redis.mget(keys)

        result = {}
        for pid, value in zip(post_ids, values):
            if value:
                result[pid] = json.loads(value)

        return result

    async def invalidate_post(self, redis: Redis, post_id: int):
        """失效帖子缓存（编辑、删除时调用）"""
        detail_key = self._get_post_detail_key(post_id)
        list_key = self._get_post_list_key(post_id)
        await redis.delete(detail_key, list_key)


# 导出服务实例
hot_rank_service = HotRankService()
post_cache_service = PostCacheService()


__all__ = ["hot_rank_service", "post_cache_service", "HotRankService", "PostCacheService"]
