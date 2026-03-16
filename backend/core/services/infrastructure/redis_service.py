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
from core.config import settings
from datetime import timezone


class HotRankService:
    """热度排行服务 - 使用 Redis ZSET 管理热门帖子、社区、用户"""

    # Redis Key 前缀
    HOT_POSTS_GLOBAL = "hot:posts:global"
    HOT_POSTS_COMMUNITY = "hot:posts:community"
    POST_INTERACTIONS = "post:interactions"  # Hash 存储交互计数

    # 新增：社区和用户热度相关
    HOT_COMMUNITIES_GLOBAL = "hot:communities:global"
    HOT_USERS_GLOBAL = "hot:users:global"
    COMMUNITY_STATS_PREFIX = "community:stats"
    USER_STATS_PREFIX = "user:stats"

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

    # ==================== 社区热度相关方法 ====================

    @staticmethod
    def _get_community_stats_key(community_id: int) -> str:
        """获取社区统计 key"""
        return f"{HotRankService.COMMUNITY_STATS_PREFIX}:{community_id}"

    @staticmethod
    def _calculate_community_hot_rank(
        member_count: int,
        post_count: int,
        recent_posts: int,  # 近7天帖子数
        created_at: datetime
    ) -> float:
        """
        计算社区热度分数

        公式: 成员权重 + 帖子权重 + 活跃度权重 + 时间衰减
        """
        # 成员对数权重（每10个成员+1分，最多5分）
        member_score = min(math.log10(max(member_count, 1)), 5)

        # 帖子数量对数权重
        post_score = min(math.log10(max(post_count, 1)), 5)

        # 近期活跃度（近7天帖子，权重更高）
        activity_score = min(recent_posts * 0.5, 3)

        # 时间衰减（社区越老，优势越小）
        epoch_seconds = int(created_at.timestamp())
        time_decay = (epoch_seconds / 45000) * 0.1

        return round(member_score + post_score + activity_score + time_decay, 7)

    async def sync_community_rank_from_db(
        self,
        redis: Redis,
        community_id: int,
        member_count: int,
        post_count: int,
        recent_posts: int,
        created_at: datetime
    ):
        """
        从数据库同步社区热度到 Redis

        用于初始化或定时同步
        """
        hot_rank = self._calculate_community_hot_rank(
            member_count=member_count,
            post_count=post_count,
            recent_posts=recent_posts,
            created_at=created_at
        )

        # 更新全局热门社区 ZSET
        await redis.zadd(self.HOT_COMMUNITIES_GLOBAL, {str(community_id): hot_rank})

        # 缓存社区统计详情
        stats_key = self._get_community_stats_key(community_id)
        await redis.hset(stats_key, mapping={
            'member_count': member_count,
            'post_count': post_count,
            'recent_posts': recent_posts,
            'hot_rank': str(hot_rank)
        })
        await redis.expire(stats_key, 3600)  # 1小时过期

    async def get_hot_community_ids(
        self,
        redis: Redis,
        limit: int = 20,
        offset: int = 0
    ) -> List[int]:
        """
        获取热门社区 ID 列表

        Args:
            redis: Redis 客户端
            limit: 返回数量
            offset: 偏移量

        Returns:
            社区 ID 列表（按热度降序）
        """
        # ZREVRANGE 返回有序集合中指定范围的成员（分数从高到低）
        community_ids = await redis.zrevrange(
            self.HOT_COMMUNITIES_GLOBAL,
            start=offset,
            end=offset + limit - 1,
        )

        return [int(cid) for cid in community_ids]

    async def remove_community(self, redis: Redis, community_id: int):
        """从热门榜中移除社区（删除时调用）"""
        await redis.zrem(self.HOT_COMMUNITIES_GLOBAL, str(community_id))
        await redis.delete(self._get_community_stats_key(community_id))

    # ==================== 用户活跃度相关方法 ====================

    @staticmethod
    def _get_user_stats_key(user_id: int) -> str:
        """获取用户统计 key"""
        return f"{HotRankService.USER_STATS_PREFIX}:{user_id}"

    @staticmethod
    def _calculate_user_hot_rank(
        karma: int,
        post_count: int,
        comment_count: int,
        recent_activity: int,  # 近7天发帖+评论数
        last_login: Optional[datetime],
        created_at: datetime
    ) -> float:
        """
        计算用户活跃度分数

        公式: Karma权重 + 贡献权重 + 近期活跃 + 登录新鲜度
        """
        # Karma 对数权重
        karma_score = min(math.log10(max(abs(karma), 1)), 5)

        # 贡献数量（发帖+评论）
        contribution_score = min(math.log10(max(post_count + comment_count, 1)), 3)

        # 近期活跃度（近7天）
        activity_score = min(recent_activity * 0.3, 2)

        # 登录新鲜度（最近登录的用户得分更高）
        if last_login:
            login_freshness = (int(last_login.timestamp()) / 45000) * 0.5
        else:
            login_freshness = 0

        return round(karma_score + contribution_score + activity_score + login_freshness, 7)

    async def sync_user_rank_from_db(
        self,
        redis: Redis,
        user_id: int,
        karma: int,
        post_count: int,
        comment_count: int,
        recent_activity: int,
        last_login: Optional[datetime],
        created_at: datetime
    ):
        """
        从数据库同步用户活跃度到 Redis

        用于初始化或定时同步
        """
        hot_rank = self._calculate_user_hot_rank(
            karma=karma,
            post_count=post_count,
            comment_count=comment_count,
            recent_activity=recent_activity,
            last_login=last_login,
            created_at=created_at
        )

        # 更新全局活跃用户 ZSET
        await redis.zadd(self.HOT_USERS_GLOBAL, {str(user_id): hot_rank})

        # 缓存用户统计详情
        stats_key = self._get_user_stats_key(user_id)
        stats_data = {
            'karma': karma,
            'post_count': post_count,
            'comment_count': comment_count,
            'recent_activity': recent_activity,
            'hot_rank': str(hot_rank)
        }
        await redis.hset(stats_key, mapping=stats_data)
        await redis.expire(stats_key, 3600)  # 1小时过期

    async def get_hot_user_ids(
        self,
        redis: Redis,
        limit: int = 20,
        offset: int = 0
    ) -> List[int]:
        """
        获取活跃用户 ID 列表

        Args:
            redis: Redis 客户端
            limit: 返回数量
            offset: 偏移量

        Returns:
            用户 ID 列表（按活跃度降序）
        """
        # ZREVRANGE 返回有序集合中指定范围的成员（分数从高到低）
        user_ids = await redis.zrevrange(
            self.HOT_USERS_GLOBAL,
            start=offset,
            end=offset + limit - 1,
        )

        return [int(uid) for uid in user_ids]

    async def remove_user(self, redis: Redis, user_id: int):
        """从热门榜中移除用户（删除时调用）"""
        await redis.zrem(self.HOT_USERS_GLOBAL, str(user_id))
        await redis.delete(self._get_user_stats_key(user_id))


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


class CommentCacheService:
    """评论树懒加载缓存服务"""

    # Redis Key 前缀
    COMMENT_DETAIL_PREFIX = "comment:detail"
    COMMENT_CHILDREN_PREFIX = "comment:children"
    COMMENT_ROOT_PREFIX = "comment:root"
    COMMENT_META_PREFIX = "comment:meta"

    # TTL 配置
    DEFAULT_TTL = getattr(settings, 'REDIS_COMMENT_TTL', 3600)  # 1小时
    META_TTL = getattr(settings, 'REDIS_COMMENT_META_TTL', 600)  # 10分钟

    # 默认加载配置
    DEFAULT_ROOT_LIMIT = 20  # 首次加载根评论数
    DEFAULT_REPLY_LIMIT = 3  # 每个根评论预加载的子评论数

    @staticmethod
    def _get_comment_detail_key(post_id: int, comment_id: int) -> str:
        """获取单条评论详情 key"""
        return f"{CommentCacheService.COMMENT_DETAIL_PREFIX}:{post_id}:{comment_id}"

    @staticmethod
    def _get_children_key(post_id: int, parent_id: int) -> str:
        """获取子评论列表 key（parent_id=0 表示根评论）"""
        if parent_id is None or parent_id == 0:
            return f"{CommentCacheService.COMMENT_ROOT_PREFIX}:{post_id}"
        return f"{CommentCacheService.COMMENT_CHILDREN_PREFIX}:{post_id}:{parent_id}"

    @staticmethod
    def _get_meta_key(post_id: int) -> str:
        """获取元数据 key"""
        return f"{CommentCacheService.COMMENT_META_PREFIX}:{post_id}"

    @staticmethod
    def _serialize_comment(comment_dict: dict) -> dict:
        """序列化评论数据（处理 datetime 等类型）"""
        serialized = {}
        for key, value in comment_dict.items():
            if value is None:
                # Convert None to empty string for Redis compatibility
                serialized[key] = ''
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, bool):
                # Convert boolean to string for Redis compatibility
                serialized[key] = str(value)
            else:
                serialized[key] = value
        return serialized

    @staticmethod
    def _deserialize_comment(hash_data: dict) -> dict:
        """反序列化评论数据"""
        result = {}
        for key, value in hash_data.items():
            if key in ('created_at', 'updated_at', 'deleted_at'):
                # Handle empty string as None for datetime fields
                result[key] = value if value is None or value == '' else datetime.fromisoformat(value)
            elif key in ('id', 'author_id', 'parent_id', 'upvotes', 'downvotes', 'score'):
                result[key] = int(value) if value and value != '' else None
            elif key == 'is_edited':
                result[key] = value.lower() == 'true' if isinstance(value, str) else bool(value)
            else:
                result[key] = value
        return result

    async def cache_comment(
        self,
        redis: Redis,
        post_id: int,
        comment_data: dict,
        ttl: Optional[int] = None
    ):
        """
        缓存单条评论内容

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            comment_data: 评论数据字典
            ttl: 过期时间（秒）
        """
        comment_id = comment_data['id']
        key = self._get_comment_detail_key(post_id, comment_id)

        serialized = self._serialize_comment(comment_data)

        await redis.hset(key, mapping=serialized)
        if ttl:
            await redis.expire(key, ttl)

    async def cache_comments_batch(
        self,
        redis: Redis,
        post_id: int,
        comments: List[dict],
        ttl: Optional[int] = None
    ):
        """
        批量缓存评论内容

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            comments: 评论数据列表
            ttl: 过期时间（秒）
        """
        pipe = redis.pipeline()
        for comment in comments:
            comment_id = comment['id']
            key = self._get_comment_detail_key(post_id, comment_id)
            serialized = self._serialize_comment(comment)
            pipe.hset(key, mapping=serialized)
            if ttl:
                pipe.expire(key, ttl)
        await pipe.execute()

    async def add_to_children_index(
        self,
        redis: Redis,
        post_id: int,
        parent_id: Optional[int],
        comment_id: int,
        score: int,
        ttl: Optional[int] = None
    ):
        """
        将评论添加到父子关系索引

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            parent_id: 父评论 ID（None 表示根评论）
            comment_id: 评论 ID
            score: 评论评分（用于排序）
            ttl: 过期时间（秒）
        """
        key = self._get_children_key(post_id, parent_id or 0)
        await redis.zadd(key, {str(comment_id): score})
        if ttl:
            await redis.expire(key, ttl)

    async def get_cached_comment(
        self,
        redis: Redis,
        post_id: int,
        comment_id: int
    ) -> Optional[dict]:
        """
        获取缓存的评论详情

        Returns:
            评论数据字典，未命中返回 None
        """
        key = self._get_comment_detail_key(post_id, comment_id)
        data = await redis.hgetall(key)

        if not data:
            return None

        return self._deserialize_comment(data)

    async def get_cached_comments_batch(
        self,
        redis: Redis,
        post_id: int,
        comment_ids: List[int]
    ) -> dict:
        """
        批量获取缓存的评论详情

        Returns:
            dict: {comment_id: comment_data}
        """
        if not comment_ids:
            return {}

        pipe = redis.pipeline()
        keys = [self._get_comment_detail_key(post_id, cid) for cid in comment_ids]
        for key in keys:
            pipe.hgetall(key)

        results = await pipe.execute()

        cached_comments = {}
        for cid, data in zip(comment_ids, results):
            if data:
                cached_comments[cid] = self._deserialize_comment(data)

        return cached_comments

    async def get_children_ids(
        self,
        redis: Redis,
        post_id: int,
        parent_id: Optional[int],
        offset: int = 0,
        limit: int = 20,
        order: str = 'desc'
    ) -> List[int]:
        """
        获取子评论 ID 列表（按 score 排序）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            parent_id: 父评论 ID（None 表示根评论）
            offset: 偏移量
            limit: 返回数量
            order: 排序方向 ('desc' 或 'asc')

        Returns:
            评论 ID 列表
        """
        key = self._get_children_key(post_id, parent_id or 0)

        # 使用 ZREVRANGE 或 ZRANGE
        if order == 'desc':
            comment_ids = await redis.zrevrange(key, start=offset, end=offset + limit - 1)
        else:
            comment_ids = await redis.zrange(key, start=offset, end=offset + limit - 1)

        return [int(cid) for cid in comment_ids]

    async def get_children_count(
        self,
        redis: Redis,
        post_id: int,
        parent_id: Optional[int]
    ) -> int:
        """获取子评论总数"""
        key = self._get_children_key(post_id, parent_id or 0)
        return await redis.zcard(key)

    async def get_post_comments(
        self,
        redis: Redis,
        post_id: int,
        root_limit: int = DEFAULT_ROOT_LIMIT,
        root_offset: int = 0,
        reply_limit: int = DEFAULT_REPLY_LIMIT,
        include_children: bool = True
    ) -> List[dict]:
        """
        获取帖子评论树（懒加载首次请求）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            root_limit: 根评论数量
            root_offset: 根评论偏移量
            reply_limit: 每个根评论预加载的子评论数量
            include_children: 是否包含子评论

        Returns:
            评论树列表（嵌套结构）
        """
        # 1. 获取根评论 ID 列表
        root_ids = await self.get_children_ids(
            redis, post_id, None,
            offset=root_offset, limit=root_limit, order='desc'
        )

        if not root_ids:
            return []

        # 2. 批量获取根评论详情
        cached_roots = await self.get_cached_comments_batch(redis, post_id, root_ids)

        # 3. 构建结果树
        result = []
        for root_id in root_ids:
            root_comment = cached_roots.get(root_id)
            if not root_comment:
                # 缓存未命中，需要从 DB 加载
                continue

            root_comment['replies'] = []
            root_comment['reply_count'] = await self.get_children_count(redis, post_id, root_id)
            root_comment['has_more_replies'] = root_comment['reply_count'] > reply_limit

            # 4. 预加载少量子评论
            if include_children and root_comment['reply_count'] > 0:
                reply_ids = await self.get_children_ids(
                    redis, post_id, root_id,
                    offset=0, limit=reply_limit, order='desc'
                )

                if reply_ids:
                    cached_replies = await self.get_cached_comments_batch(redis, post_id, reply_ids)

                    for reply_id in reply_ids:
                        reply = cached_replies.get(reply_id)
                        if reply:
                            reply['replies'] = []
                            reply['reply_count'] = await self.get_children_count(redis, post_id, reply_id)
                            reply['has_more_replies'] = reply['reply_count'] > 0
                            root_comment['replies'].append(reply)

            result.append(root_comment)

        return result

    async def get_comment_replies(
        self,
        redis: Redis,
        post_id: int,
        parent_id: int,
        offset: int = 0,
        limit: int = 20
    ) -> dict:
        """
        获取子评论列表（点击展开时调用）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            parent_id: 父评论 ID
            offset: 偏移量
            limit: 返回数量

        Returns:
            {
                'replies': List[Dict],  # 子评论列表
                'total': int,           # 总数
                'has_more': bool        # 是否有更多
            }
        """
        # 获取子评论 ID 列表
        reply_ids = await self.get_children_ids(
            redis, post_id, parent_id,
            offset=offset, limit=limit, order='desc'
        )

        # 批量获取详情
        cached_replies = await self.get_cached_comments_batch(redis, post_id, reply_ids)

        # 构建结果
        replies = []
        for reply_id in reply_ids:
            reply = cached_replies.get(reply_id)
            if reply:
                reply['replies'] = []
                reply['reply_count'] = await self.get_children_count(redis, post_id, reply_id)
                reply['has_more_replies'] = reply['reply_count'] > 0
                replies.append(reply)

        total = await self.get_children_count(redis, post_id, parent_id)
        has_more = offset + limit < total

        return {
            'replies': replies,
            'total': total,
            'has_more': has_more
        }

    async def build_cache_from_db(
        self,
        redis: Redis,
        post_id: int,
        comments_data: List[dict]
    ):
        """
        从数据库重建缓存（Cache-Aside 兜底）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            comments_data: 从数据库查询的评论列表（需包含所有字段）
        """
        pipe = redis.pipeline()

        # 1. 批量缓存评论详情
        for comment in comments_data:
            comment_id = comment['id']
            detail_key = self._get_comment_detail_key(post_id, comment_id)
            serialized = self._serialize_comment(comment)
            pipe.hset(detail_key, mapping=serialized)
            pipe.expire(detail_key, self.DEFAULT_TTL)

            # 2. 构建父子关系索引
            parent_id = comment.get('parent_id') or 0
            children_key = self._get_children_key(post_id, parent_id)
            score = comment.get('score', 0)
            pipe.zadd(children_key, {str(comment_id): score})
            pipe.expire(children_key, self.DEFAULT_TTL)

        # 3. 更新元数据
        meta_key = self._get_meta_key(post_id)
        root_comments = [c for c in comments_data if not c.get('parent_id')]
        pipe.hset(meta_key, 'total_count', len(comments_data))
        pipe.hset(meta_key, 'root_count', len(root_comments))
        pipe.hset(meta_key, 'last_updated', datetime.now(timezone.utc).isoformat())
        pipe.expire(meta_key, self.META_TTL)

        await pipe.execute()

    async def invalidate_comment(
        self,
        redis: Redis,
        post_id: int,
        comment_id: int,
        parent_id: Optional[int] = None
    ):
        """
        失效评论缓存（编辑、删除时调用）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            comment_id: 评论 ID
            parent_id: 父评论 ID（可选，用于优化）
        """
        # 1. 删除评论详情
        detail_key = self._get_comment_detail_key(post_id, comment_id)
        await redis.delete(detail_key)

        # 2. 从父评论的子评论列表中移除
        children_key = self._get_children_key(post_id, parent_id or 0)
        await redis.zrem(children_key, str(comment_id))

        # 3. 如果有子评论，也需要清理子评论索引
        # 注意：这需要递归处理或使用更复杂的策略
        # 简化版：只删除直接索引，依赖 TTL 清理深层缓存

    async def invalidate_post_comments(
        self,
        redis: Redis,
        post_id: int
    ):
        """
        失效整个帖子的评论缓存（帖子删除时调用）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
        """
        # 使用 SCAN 查找所有相关 key
        pattern = f"{self.COMMENT_DETAIL_PREFIX}:{post_id}:*"
        keys = []
        async for key in redis.scan_iter(match=pattern, count=100):
            keys.append(key)

        # 同时删除关系索引和元数据
        keys.append(f"{self.COMMENT_ROOT_PREFIX}:{post_id}")
        keys.append(f"{self.COMMENT_META_PREFIX}:{post_id}")

        # 扫描子评论索引
        children_pattern = f"{self.COMMENT_CHILDREN_PREFIX}:{post_id}:*"
        async for key in redis.scan_iter(match=children_pattern, count=100):
            keys.append(key)

        if keys:
            await redis.delete(*keys)

    async def get_meta(
        self,
        redis: Redis,
        post_id: int
    ) -> Optional[dict]:
        """获取帖子评论元数据"""
        key = self._get_meta_key(post_id)
        data = await redis.hgetall(key)

        if not data:
            return None

        return {
            'total_count': int(data.get('total_count', 0)),
            'root_count': int(data.get('root_count', 0)),
            'last_updated': data.get('last_updated')
        }


# 导出服务实例
hot_rank_service = HotRankService()
post_cache_service = PostCacheService()
comment_cache_service = CommentCacheService()


__all__ = [
    "hot_rank_service",
    "post_cache_service",
    "comment_cache_service",
    "HotRankService",
    "PostCacheService",
    "CommentCacheService"
]
