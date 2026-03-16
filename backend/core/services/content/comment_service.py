"""
@Created on : 2026/3/15
@Author: wrn
@Des: 评论服务 - 评论 CRUD + Redis 缓存 + 树形结构
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from redis.asyncio import Redis
from models.user import User
from models.comment import Comment
from models.post import Post
from core.services.infrastructure.redis_service import comment_cache_service
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class CommentService:
    """评论服务 - Redis 缓存 + 树形结构"""

    async def create_comment(
        self,
        redis: Redis,
        post_id: int,
        user: User,
        content: str,
        parent_id: Optional[int] = None
    ) -> dict:
        """
        创建评论并更新 Redis 缓存

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            user: 当前用户
            content: 评论内容
            parent_id: 父评论 ID（可选）

        Returns:
            dict: 创建的评论数据
        """
        # 1. 创建评论
        comment = await Comment.create(
            content=content,
            post_id=post_id,
            author_id=user.id,
            parent_id=parent_id
        )

        # 2. 缓存新评论
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'author_id': comment.author_id,
            'author_name': user.username,
            'author_avatar': user.avatar,
            'parent_id': comment.parent_id,
            'upvotes': comment.upvotes,
            'downvotes': comment.downvotes,
            'score': comment.score,
            'deleted_at': comment.deleted_at,
            'is_edited': comment.is_edited,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at,
        }

        await comment_cache_service.cache_comment(
            redis=redis,
            post_id=comment.post_id,
            comment_data=comment_data
        )

        # 3. 添加到索引
        await comment_cache_service.add_to_children_index(
            redis=redis,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            comment_id=comment.id,
            score=comment.score
        )

        # 4. 构建响应
        return {
            'id': comment.id,
            'content': comment.content,
            'author_id': comment.author_id,
            'author_name': user.username,
            'author_avatar': user.avatar,
            'parent_id': comment.parent_id,
            'upvotes': comment.upvotes,
            'downvotes': comment.downvotes,
            'score': comment.score,
            'is_edited': comment.is_edited,
            'deleted_at': comment.deleted_at,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at,
            'replies': [],
            'reply_count': 0,
            'has_more_replies': False,
        }

    async def get_comment_tree(
        self,
        redis: Redis,
        post_id: int,
        root_offset: int = 0,
        root_limit: int = 20,
        reply_limit: int = 3,
        include_children: bool = True
    ) -> dict:
        """
        获取评论树（懒加载）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            root_offset: 根评论偏移量
            root_limit: 根评论数量
            reply_limit: 每个根评论预加载的子评论数
            include_children: 是否包含子评论

        Returns:
            dict: 评论树数据
        """
        # 1. 尝试从 Redis 获取
        comments_tree = await comment_cache_service.get_post_comments(
            redis=redis,
            post_id=post_id,
            root_limit=root_limit,
            root_offset=root_offset,
            reply_limit=reply_limit,
            include_children=include_children
        )

        # 2. 如果缓存为空，从数据库加载
        if not comments_tree:
            from tortoise import connections

            # 2.1 使用 SQL CTE 查询所有评论
            conn = connections.get("default")
            sql = """
            WITH RECURSIVE comment_tree AS (
                SELECT
                    c.id,
                    c.content,
                    c.author_id,
                    c.parent_id,
                    c.upvotes,
                    c.downvotes,
                    c.score,
                    c.deleted_at,
                    c.is_edited,
                    c.created_at,
                    c.updated_at,
                    u.username as author_name,
                    u.avatar as author_avatar,
                    0 as depth
                FROM comments c
                JOIN users u ON c.author_id = u.id
                WHERE c.post_id = $1 AND c.parent_id IS NULL

                UNION ALL

                SELECT
                    c.id,
                    c.content,
                    c.author_id,
                    c.parent_id,
                    c.upvotes,
                    c.downvotes,
                    c.score,
                    c.deleted_at,
                    c.is_edited,
                    c.created_at,
                    c.updated_at,
                    u.username as author_name,
                    u.avatar as author_avatar,
                    ct.depth + 1
                FROM comments c
                JOIN users u ON c.author_id = u.id
                JOIN comment_tree ct ON c.parent_id = ct.id
            )
            SELECT * FROM comment_tree ORDER BY depth, created_at;
            """

            flat_comments = await conn.execute_query_dict(sql, [post_id])

            if flat_comments:
                # 2.2 重建 Redis 缓存
                await comment_cache_service.build_cache_from_db(
                    redis=redis,
                    post_id=post_id,
                    comments_data=flat_comments
                )

                # 2.3 再次从缓存获取（这次应该命中）
                comments_tree = await comment_cache_service.get_post_comments(
                    redis=redis,
                    post_id=post_id,
                    root_limit=root_limit,
                    root_offset=root_offset,
                    reply_limit=reply_limit,
                    include_children=include_children
                )

        return comments_tree if comments_tree else []

    async def get_comment_replies(
        self,
        redis: Redis,
        post_id: int,
        parent_id: int,
        offset: int = 0,
        limit: int = 20
    ) -> dict:
        """
        获取子评论列表

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            parent_id: 父评论 ID
            offset: 偏移量
            limit: 返回数量

        Returns:
            dict: 子评论列表数据
        """
        # 1. 尝试从 Redis 获取
        result = await comment_cache_service.get_comment_replies(
            redis=redis,
            post_id=post_id,
            parent_id=parent_id,
            offset=offset,
            limit=limit
        )

        # 2. 缓存未命中，从数据库加载
        if not result['replies']:
            from tortoise import connections

            # 查询子评论
            conn = connections.get("default")

            sql = """
            SELECT
                c.id,
                c.content,
                c.author_id,
                c.parent_id,
                c.upvotes,
                c.downvotes,
                c.score,
                c.deleted_at,
                c.is_edited,
                c.created_at,
                c.updated_at,
                u.username as author_name,
                u.avatar as author_avatar
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = $1 AND c.parent_id = $2
            ORDER BY c.score DESC, c.created_at ASC
            LIMIT $3 OFFSET $4;
            """

            replies_data = await conn.execute_query_dict(sql, [post_id, parent_id, limit, offset])

            if replies_data:
                # 重建缓存
                await comment_cache_service.build_cache_from_db(
                    redis=redis,
                    post_id=post_id,
                    comments_data=replies_data
                )

                # 再次获取
                result = await comment_cache_service.get_comment_replies(
                    redis=redis,
                    post_id=post_id,
                    parent_id=parent_id,
                    offset=offset,
                    limit=limit
                )

        return result if result else {'replies': [], 'total': 0, 'has_more': False}

    async def update_comment(
        self,
        redis: Redis,
        comment_id: int,
        user: User,
        content: str
    ) -> dict:
        """
        更新评论

        Args:
            redis: Redis 客户端
            comment_id: 评论 ID
            user: 当前用户
            content: 新内容

        Returns:
            dict: 更新的评论数据

        Raises:
            Returns {"error": "..."} on failure
        """
        comment = await Comment.get_or_none(id=comment_id).prefetch_related('author')

        if not comment:
            return {"error": "评论不存在"}

        if comment.author_id != user.id:
            return {"error": "无权编辑此评论"}

        if comment.deleted_at:
            return {"error": "无法编辑已删除的评论"}

        await Comment.filter(id=comment_id).update(
            content=content,
            is_edited=True
        )
        await comment.refresh_from_db()

        # 失效缓存
        await comment_cache_service.invalidate_comment(
            redis=redis,
            post_id=comment.post_id,
            comment_id=comment_id,
            parent_id=comment.parent_id
        )

        # 构建响应数据（添加 author_name 和 author_avatar）
        return {
            'id': comment.id,
            'content': comment.content,
            'author_id': comment.author_id,
            'author_name': comment.author.username if comment.author else user.username,
            'author_avatar': comment.author.avatar if comment.author else user.avatar,
            'parent_id': comment.parent_id,
            'upvotes': comment.upvotes,
            'downvotes': comment.downvotes,
            'score': comment.score,
            'is_edited': comment.is_edited,
            'deleted_at': comment.deleted_at,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at,
            'replies': [],
            'reply_count': 0,
            'has_more_replies': False,
        }

    async def delete_comment(
        self,
        redis: Redis,
        comment_id: int,
        user: User,
        reason: Optional[str] = None,
        is_moderator: bool = False
    ) -> dict:
        """
        删除评论

        Args:
            redis: Redis 客户端
            comment_id: 评论 ID
            user: 当前用户
            reason: 删除原因
            is_moderator: 是否为版主操作

        Returns:
            dict: 删除结果

        Raises:
            Returns {"error": "..."} on failure
        """
        comment = await Comment.get_or_none(id=comment_id)

        if not comment:
            return {"error": "评论不存在"}

        await Comment.filter(id=comment_id).update(
            deleted_at=datetime.now(timezone.utc)
        )

        # 失效缓存
        await comment_cache_service.invalidate_comment(
            redis=redis,
            post_id=comment.post_id,
            comment_id=comment_id,
            parent_id=comment.parent_id
        )

        return {"message": "评论删除成功"}

    async def restore_comment(
        self,
        redis: Redis,
        comment_id: int,
        user: User
    ) -> dict:
        """
        恢复已删除的评论

        Args:
            redis: Redis 客户端
            comment_id: 评论 ID
            user: 当前用户

        Returns:
            dict: 恢复结果

        Raises:
            Returns {"error": "..."} on failure
        """
        comment = await Comment.get_or_none(id=comment_id)

        if not comment:
            return {"error": "评论不存在"}

        if comment.author_id != user.id and not user.is_superuser:
            return {"error": "无权恢复此评论"}

        await Comment.filter(id=comment_id).update(deleted_at=None)

        # 失效缓存
        await comment_cache_service.invalidate_comment(
            redis=redis,
            post_id=comment.post_id,
            comment_id=comment_id,
            parent_id=comment.parent_id
        )

        return {"message": "评论恢复成功"}


# 导出服务实例
comment_service = CommentService()

__all__ = ["CommentService", "comment_service"]
