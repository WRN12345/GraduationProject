"""
@Created on : 2025/12/8
@Author: wrn
@Des: 全文搜索路由
"""

from fastapi import APIRouter, Query
from typing import List, Optional
from backend.models.post import Post
from backend.models.comment import Comment
from backend.models.user import User
from tortoise import connections

router = APIRouter(tags=["搜索"])

@router.get("/search/posts", summary="搜索帖子")
async def search_posts(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
):
    """
    全文搜索帖子（标题和内容）
    使用 PostgreSQL 全文搜索和相关性排序
    """
    if not q or len(q.strip()) < 2:
        return []

    # 构建搜索查询
    # ts_rank: 计算相关性分数
    # plainto_tsquery: 将搜索文本转换为 tsquery
    sql = """
    SELECT
        p.id,
        p.title,
        p.content,
        p.score,
        p.hot_rank,
        p.author_id,
        p.community_id,
        p.upvotes,
        p.downvotes,
        p.is_edited,
        p.deleted_at,
        p.created_at,
        p.updated_at,
        ts_rank(p.search_vector, plainto_tsquery('english', $1)) as rank
    FROM posts p
    WHERE p.search_vector @@ plainto_tsquery('english', $1)
        AND p.deleted_at IS NULL
    """

    params = [q]

    if community_id:
        sql += " AND p.community_id = $2"
        params.append(community_id)

    sql += " ORDER BY rank DESC, p.created_at DESC"
    sql += f" LIMIT {limit} OFFSET {skip}"

    conn = connections.get("default")
    results = await conn.execute_query_dict(sql, params)

    return results

@router.get("/search/comments", summary="搜索评论")
async def search_comments(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    skip: int = 0,
    limit: int = 50,
):
    """
    搜索评论（通过内容）
    使用简单的 LIKE 搜索（可以升级为全文搜索）
    """
    if not q or len(q.strip()) < 2:
        return []

    # 使用 LIKE 进行简单搜索（可以后续升级为全文搜索）
    comments = await Comment.filter(
        content__icontains=q,
        deleted_at__isnull=True
    ).order_by("-created_at").offset(skip).limit(limit)

    return comments

@router.get("/search/users", summary="搜索用户")
async def search_users(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    skip: int = 0,
    limit: int = 20,
):
    """
    搜索用户（通过用户名或昵称）
    """
    if not q or len(q.strip()) < 2:
        return []

    users = await User.filter(
        username__icontains=q
    ).filter(
        is_active=True
    ).offset(skip).limit(limit)

    return users

@router.get("/search", summary="统一搜索接口")
async def search_all(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    skip: int = 0,
    limit: int = 10,
):
    """
    统一搜索接口
    同时搜索帖子、评论和用户，返回综合结果
    """
    import asyncio

    tasks = [
        search_posts(q, skip, limit),
        search_comments(q, skip, limit),
        search_users(q, skip, limit),
    ]

    posts, comments, users = await asyncio.gather(*tasks)

    return {
        "posts": posts,
        "comments": comments,
        "users": users,
    }
