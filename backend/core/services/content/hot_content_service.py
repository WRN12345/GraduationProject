"""
@Created on : 2026.3.16
@Author: wrn
@Des: 热门内容聚合服务 - 侧边栏热门内容（帖子、社区、用户）
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from redis.asyncio import Redis

from core.services.infrastructure.redis_service import hot_rank_service
from models.post import Post
from models.community import Community
from models.user import User


class HotContentService:
    """热门内容聚合服务"""

    async def get_sidebar_hot_content(
        self,
        redis: Redis,
        limit: int = 10,
        community_id: Optional[int] = None
    ) -> Dict[str, List[Any]]:
        """
        获取侧边栏热门内容（聚合）

        Args:
            redis: Redis 客户端
            limit: 每类内容返回数量（5-20）
            community_id: 社区 ID（可选，用于获取特定社区的热门帖子）

        Returns:
            {
                "hot_posts": [...],      # 热门帖子
                "hot_communities": [...], # 热门社区
                "hot_users": [...]       # 活跃用户
            }
        """
        # 并发查询三类内容
        posts, communities, users = await asyncio.gather(
            self._get_hot_posts(redis, limit, community_id),
            self._get_hot_communities(redis, limit),
            self._get_hot_users(redis, limit)
        )

        return {
            "hot_posts": posts,
            "hot_communities": communities,
            "hot_users": users
        }

    async def _get_hot_posts(
        self,
        redis: Redis,
        limit: int,
        community_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取热门帖子"""
        # 获取热门帖子 ID 列表
        post_ids = await hot_rank_service.get_hot_post_ids(
            redis, limit=limit, offset=0, community_id=community_id
        )

        if not post_ids:
            return []

        # 批量查询帖子详情
        posts = await Post.filter(
            id__in=post_ids,
            deleted_at__isnull=True
        ).prefetch_related('author', 'community')

        # 按 Redis 排序顺序重新排列
        posts_dict = {post.id: post for post in posts}
        sorted_posts = []
        for pid in post_ids:
            if pid in posts_dict:
                post = posts_dict[pid]
                sorted_posts.append({
                    "id": post.id,
                    "title": post.title,
                    "score": post.score,
                    "hot_rank": post.hot_rank,
                    "community_name": post.community.name if post.community else "未知",
                    "author_username": post.author.username if post.author else "匿名",
                    "created_at": post.created_at
                })

        return sorted_posts

    async def _get_hot_communities(
        self,
        redis: Redis,
        limit: int
    ) -> List[Dict[str, Any]]:
        """获取热门社区"""
        # 获取热门社区 ID 列表
        community_ids = await hot_rank_service.get_hot_community_ids(
            redis, limit=limit, offset=0
        )

        if not community_ids:
            return []

        # 批量查询社区详情
        communities = await Community.filter(id__in=community_ids)

        # 按 Redis 排序顺序重新排列
        communities_dict = {community.id: community for community in communities}
        sorted_communities = []
        for cid in community_ids:
            if cid in communities_dict:
                community = communities_dict[cid]
                sorted_communities.append({
                    "id": community.id,
                    "name": community.name,
                    "description": community.description or "",
                    "member_count": community.member_count,
                    "post_count": getattr(community, 'post_count', 0) if hasattr(community, 'post_count') else 0,
                    "hot_rank": 0.0  # 可以从 Redis 缓存获取
                })

        return sorted_communities

    async def _get_hot_users(
        self,
        redis: Redis,
        limit: int
    ) -> List[Dict[str, Any]]:
        """获取活跃用户"""
        # 获取活跃用户 ID 列表
        user_ids = await hot_rank_service.get_hot_user_ids(
            redis, limit=limit, offset=0
        )

        if not user_ids:
            return []

        # 批量查询用户详情
        users = await User.filter(id__in=user_ids, is_active=True)

        # 按 Redis 排序顺序重新排列
        users_dict = {user.id: user for user in users}
        sorted_users = []
        for uid in user_ids:
            if uid in users_dict:
                user = users_dict[uid]
                sorted_users.append({
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "karma": user.karma,
                    "post_count": getattr(user, 'post_count', 0) if hasattr(user, 'post_count') else 0,
                    "comment_count": getattr(user, 'comment_count', 0) if hasattr(user, 'comment_count') else 0,
                    "hot_rank": 0.0  # 可以从 Redis 缓存获取
                })

        return sorted_users

    async def update_community_stats(
        self,
        redis: Redis,
        community_id: int
    ):
        """
        更新社区统计数据和热度

        在帖子创建/删除时调用
        """
        from tortoise.functions import Count
        from models.post import Post

        community = await Community.get_or_none(id=community_id)
        if not community:
            return

        # 计算帖子总数
        post_count = await Post.filter(
            community_id=community_id,
            deleted_at__isnull=True
        ).count()

        # 计算近7天帖子数
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_posts = await Post.filter(
            community_id=community_id,
            deleted_at__isnull=True,
            created_at__gte=seven_days_ago
        ).count()

        # 更新数据库字段
        if hasattr(community, 'post_count'):
            community.post_count = post_count
        if hasattr(community, 'last_active_at'):
            community.last_active_at = datetime.now(timezone.utc)
        await community.save()

        # 同步到 Redis
        await hot_rank_service.sync_community_rank_from_db(
            redis=redis,
            community_id=community_id,
            member_count=community.member_count,
            post_count=post_count,
            recent_posts=recent_posts,
            created_at=community.created_at
        )

    async def update_user_stats(
        self,
        redis: Redis,
        user_id: int
    ):
        """
        更新用户统计数据和活跃度

        在帖子/评论创建时调用
        """
        from models.post import Post
        from models.comment import Comment

        user = await User.get_or_none(id=user_id)
        if not user:
            return

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
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
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

        # 更新数据库字段
        if hasattr(user, 'post_count'):
            user.post_count = post_count
        if hasattr(user, 'comment_count'):
            user.comment_count = comment_count
        if hasattr(user, 'last_active_at'):
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


# 导出服务实例
hot_content_service = HotContentService()


__all__ = [
    "HotContentService",
    "hot_content_service"
]
