"""
@Created on : 2026/3/15
@Author: wrn
@Des: 搜索服务 - PostgreSQL 全文搜索
"""
from typing import Optional
from tortoise.expressions import Q
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
        搜索帖子（全文搜索 - zhparser 中文分词）

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

        # PostgreSQL 全文搜索查询 (使用 zhparser 中文分词)
        # 关联查询 author 和 community 信息，以及评论数
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
            ) as highlighted_content,
            -- 作者信息
            u.username as author_username,
            u.avatar as author_avatar,
            u.nickname as author_nickname,
            -- 社区信息
            c.name as community_name,
            -- 评论数
            COALESCE(pc.comment_count, 0) as comment_count
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        LEFT JOIN communities c ON p.community_id = c.id
        LEFT JOIN (
            SELECT post_id, COUNT(*) as comment_count
            FROM comments
            WHERE deleted_at IS NULL
            GROUP BY post_id
        ) pc ON p.id = pc.post_id
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

        # 转换结果为前端期望的嵌套对象格式
        transformed_results = []
        for r in results:
            transformed_results.append({
                "id": r.get("id"),
                "title": r.get("title"),
                "content": r.get("content"),
                "author_id": r.get("author_id"),
                "author": {
                    "id": r.get("author_id"),
                    "username": r.get("author_username") or "",
                    "nickname": r.get("author_nickname"),
                    "avatar": r.get("author_avatar")
                },
                "community_id": r.get("community_id"),
                "community": {
                    "id": r.get("community_id"),
                    "name": r.get("community_name") or ""
                } if r.get("community_id") else None,
                "score": r.get("score"),
                "upvotes": r.get("upvotes"),
                "downvotes": r.get("downvotes"),
                "hot_rank": r.get("hot_rank"),
                "created_at": r.get("created_at"),
                "updated_at": r.get("updated_at"),
                "comment_count": r.get("comment_count") or 0,
                "headline": r.get("highlighted_title") or r.get("highlighted_content"),
            })

        return {
            "results": transformed_results,
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

        # 合并查询：同时搜索用户名和昵称（使用 Q 表达式）
        users = await User.filter(
            Q(username__icontains=query_str) | Q(nickname__icontains=query_str),
            is_active=True
        ).distinct().all()

        # 手动分页
        total = len(users)
        paginated_users = users[skip:skip + limit]

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
        ).prefetch_related('author', 'post').offset(skip).limit(limit)

        total = await Comment.filter(
            content__icontains=query_str
        ).filter(
            deleted_at__isnull=True
        ).count()

        # 转换为字典格式，包含完整的作者、帖子和投票信息
        results = []
        for comment in comments:
            author = comment.author
            post = comment.post
            results.append({
                "id": comment.id,
                "content": comment.content,
                "author_id": comment.author_id,
                "author": {
                    "id": author.id if author else None,
                    "username": author.username if author else "",
                    "nickname": author.nickname if author else "",
                    "avatar": author.avatar if author else None
                } if author else None,
                "post_id": comment.post_id,
                "post": {
                    "id": post.id if post else None,
                    "title": post.title if post else ""
                } if post else None,
                "upvotes": comment.upvotes,
                "downvotes": comment.downvotes,
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
