"""
@Created on : 2026/3/15
@Author: wrn
@Des: 搜索服务 - PostgreSQL 全文搜索
"""
from typing import Optional
from models.post import Post
from models.user import User
from models.comment import Comment
from tortoise import connections
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务 - PostgreSQL 全文搜索"""

    async def search_posts(
        self,
        query: str,
        community_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        搜索帖子（全文搜索）

        Args:
            query: 搜索关键词
            community_id: 社区 ID 过滤
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 搜索结果
        """
        if not query or len(query.strip()) < 1:
            return {"results": [], "total": 0}

        # PostgreSQL 全文搜索查询
        sql = """
        SELECT
            p.id,
            p.title,
            p.content,
            p.author_id,
            p.community_id,
            p.score,
            p.upvotes,
            p.downvotes,
            p.hot_rank,
            p.created_at,
            p.updated_at,
            ts_rank(p.search_vector, plainto_tsquery('zhcfg', $1)) as rank,
            ts_headline(
                p.title,
                plainto_tsquery('zhcfg', $1),
                'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15'
            ) as highlighted_title,
            ts_headline(
                p.content,
                plainto_tsquery('zhcfg', $1),
                'StartSel=<mark>, StopSel=</mark>, MaxWords=60, MinWords=30'
            ) as highlighted_content
        FROM posts p
        WHERE p.search_vector @@ plainto_tsquery('zhcfg', $1)
            AND p.deleted_at IS NULL
        """

        params = [query.strip()]

        if community_id:
            sql += " AND p.community_id = $2"
            params.append(community_id)

        # 按相关性和创建时间排序
        sql += " ORDER BY rank DESC, p.created_at DESC"
        sql += " LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
        params.extend([limit, skip])

        # 同时获取总数
        count_sql = """
        SELECT COUNT(*) as total
        FROM posts p
        WHERE p.search_vector @@ plainto_tsquery('zhcfg', $1)
            AND p.deleted_at IS NULL
        """
        if community_id:
            count_sql += " AND p.community_id = $2"

        # 执行搜索和计数
        results = await connections.get("default").execute_query_dict(sql, params)
        count_result = await connections.get("default").execute_query_dict(
            count_sql,
            params[:2] if community_id else params[:1]
        )
        total = count_result[0]['total'] if count_result else 0

        return {
            "results": results,
            "total": total,
            "query": query.strip()
        }

    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        搜索用户

        Args:
            query: 搜索关键词
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 搜索结果
        """
        if not query or len(query.strip()) < 1:
            return {"results": [], "total": 0}

        query_str = query.strip()

        # 搜索活跃用户（按用户名）
        users = await User.filter(
            username__icontains=query_str
        ).filter(
            is_active=True
        ).all()

        # 同时搜索昵称
        users_by_nickname = await User.filter(
            nickname__icontains=query_str
        ).filter(
            is_active=True
        ).all()

        # 合并结果并去重
        seen = set()
        unique_users = []
        for user in users + users_by_nickname:
            if user.id not in seen:
                seen.add(user.id)
                unique_users.append(user)

        # 手动分页
        total = len(unique_users)
        paginated_users = unique_users[skip:skip + limit]

        # 转换为字典格式
        results = [
            {
                "id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "karma": u.karma,
                "avatar": u.avatar
            }
            for u in paginated_users
        ]

        return {
            "results": results,
            "total": total,
            "query": query_str
        }

    async def search_comments(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        搜索评论

        Args:
            query: 搜索关键词
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 搜索结果
        """
        if not query or len(query.strip()) < 1:
            return {"results": [], "total": 0}

        # 简单的 LIKE 搜索（适合评论场景）
        query_str = query.strip()

        comments = await Comment.filter(
            content__icontains=query_str
        ).filter(
            deleted_at__isnull=True
        ).prefetch_related('author').offset(skip).limit(limit)

        total = await Comment.filter(
            content__icontains=query_str
        ).filter(
            deleted_at__isnull=True
        ).count()

        # 转换为字典格式
        results = []
        for comment in comments:
            results.append({
                "id": comment.id,
                "content": comment.content,
                "author_id": comment.author_id,
                "author_name": comment.author.username if comment.author else "",
                "post_id": comment.post_id,
                "score": comment.score,
                "created_at": comment.created_at
            })

        return {
            "results": results,
            "total": total,
            "query": query_str
        }


# 导出服务实例
search_service = SearchService()

__all__ = ["SearchService", "search_service"]
