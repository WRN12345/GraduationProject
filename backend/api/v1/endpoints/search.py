"""
@Created on : 2025/12/8
@Author: wrn
@Des: 全文搜索路由（使用 PostgreSQL 全文搜索）
"""

from fastapi import APIRouter, Query
from typing import Optional
import asyncio
from backend.models.post import Post
from backend.models.user import User
from backend.models.comment import Comment
from backend.schemas import search as search_schemas
from tortoise import connections

router = APIRouter(tags=["搜索"])


@router.get("/search/posts", summary="搜索帖子（全文搜索）")
async def search_posts(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
):
    """
    全文搜索帖子（标题和内容）

    功能特性：
    - 使用 GIN 索引加速搜索
    - plainto_tsquery 处理用户输入
    - ts_headline 生成高亮 HTML
    - 按相关性排序
    """
    if not q or len(q.strip()) < 1:
        return {"results": [], "total": 0}

    # PostgreSQL 全文搜索查询
    # 使用 plainto_tsquery 将用户输入转换为 tsquery
    # 使用 ts_headline 生成搜索结果高亮
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

    params = [q.strip()]

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

    conn = connections.get("default")

    # 执行搜索和计数
    results = await conn.execute_query_dict(sql, params)
    count_result = await conn.execute_query_dict(count_sql, params[:2] if community_id else params[:1])
    total = count_result[0]['total'] if count_result else 0

    return {
        "results": results,
        "total": total,
        "query": q.strip()
    }


@router.get("/search/users", summary="搜索用户")
async def search_users(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = 0,
    limit: int = 20,
):
    """
    搜索用户（用户名或昵称）
    使用简单的 LIKE 搜索（适合用户名场景）
    """
    if not q or len(q.strip()) < 1:
        return {"results": [], "total": 0}

    query = q.strip()

    # 搜索活跃用户
    users = await User.filter(
        username__icontains=query
    ).filter(
        is_active=True
    ).all()

    # 同时搜索昵称
    users_by_nickname = await User.filter(
        nickname__icontains=query
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
            "is_superuser": u.is_superuser,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in paginated_users
    ]

    return {
        "results": results,
        "total": total,
        "query": query
    }


@router.get("/search", summary="搜索建议（快速预览）")
async def search_suggestions(
    q: str = Query(..., min_length=1, description="搜索关键词"),
):
    """
    搜索建议接口

    返回帖子、用户的前 3 条匹配结果，用于搜索框下拉建议
    不做聚合，只返回快速预览
    """
    if not q or len(q.strip()) < 1:
        return {
            "posts": [],
            "users": [],
            "query": q.strip()
        }

    import asyncio

    # 并发搜索各个类型（每个只取前 3 条）
    posts_task = search_posts(q, 0, 3)
    users_task = search_users(q, 0, 3)

    posts_res, users_res = await asyncio.gather(
        posts_task,
        users_task,
        return_exceptions=True
    )

    return {
        "posts": posts_res["results"] if not isinstance(posts_res, Exception) else [],
        "users": users_res["results"] if not isinstance(users_res, Exception) else [],
        "query": q.strip(),
        "totals": {
            "posts": posts_res["total"] if not isinstance(posts_res, Exception) else 0,
            "users": users_res["total"] if not isinstance(users_res, Exception) else 0,
        }
    }


@router.get("/search/comments", summary="搜索评论（全文搜索）")
async def search_comments(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = 0,
    limit: int = 20,
):
    """
    全文搜索评论内容

    功能特性：
    - 使用 GIN 索引加速搜索
    - plainto_tsquery 处理用户输入
    - ts_headline 生成高亮 HTML
    - 按相关性排序
    """
    if not q or len(q.strip()) < 1:
        return {"results": [], "total": 0}

    # PostgreSQL 全文搜索查询
    sql = """
    SELECT
        c.id,
        c.content,
        c.post_id,
        c.author_id,
        c.score,
        c.upvotes,
        c.downvotes,
        c.created_at,
        c.updated_at,
        ts_rank(c.search_vector, plainto_tsquery('zhcfg', $1)) as rank,
        ts_headline(
            c.content,
            plainto_tsquery('zhcfg', $1),
            'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15'
        ) as highlighted_content
    FROM comments c
    WHERE c.search_vector @@ plainto_tsquery('zhcfg', $1)
        AND c.deleted_at IS NULL
    ORDER BY rank DESC, c.created_at DESC
    LIMIT $2 OFFSET $3
    """

    # 同时获取总数
    count_sql = """
    SELECT COUNT(*) as total
    FROM comments c
    WHERE c.search_vector @@ plainto_tsquery('zhcfg', $1)
        AND c.deleted_at IS NULL
    """

    conn = connections.get("default")

    # 执行搜索和计数
    results = await conn.execute_query_dict(sql, [q.strip(), limit, skip])
    count_result = await conn.execute_query_dict(count_sql, [q.strip()])
    total = count_result[0]['total'] if count_result else 0

    return {
        "results": results,
        "total": total,
        "query": q.strip()
    }


@router.get("/search/all", summary="统一搜索（帖子+评论+用户）")
async def search_all(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = 0,
    limit: int = Query(10, ge=1, le=50, description="每种类型返回的数量"),
):
    """
    统一搜索接口 - 同时搜索帖子、评论、用户

    返回结构包含：
    - posts: 帖子搜索结果
    - comments: 评论搜索结果
    - users: 用户搜索结果
    - total: 总结果数
    """
    if not q or len(q.strip()) < 1:
        return {
            "posts": [],
            "comments": [],
            "users": [],
            "total": 0,
            "query": ""
        }

    query = q.strip()

    # 并发执行三个搜索
    posts_task = _fetch_posts_search(query, skip, limit)
    comments_task = _fetch_comments_search(query, skip, limit)
    users_task = _fetch_users_search(query, skip, limit)

    posts_res, comments_res, users_res = await asyncio.gather(
        posts_task,
        comments_task,
        users_task,
        return_exceptions=True
    )

    # 处理异常结果
    posts_result = posts_res if not isinstance(posts_res, Exception) else {"results": [], "total": 0}
    comments_result = comments_res if not isinstance(comments_res, Exception) else {"results": [], "total": 0}
    users_result = users_res if not isinstance(users_res, Exception) else {"results": [], "total": 0}

    total = posts_result.get("total", 0) + comments_result.get("total", 0) + users_result.get("total", 0)

    return {
        "posts": posts_result.get("results", []),
        "comments": comments_result.get("results", []),
        "users": users_result.get("results", []),
        "total": total,
        "query": query
    }


async def _fetch_posts_search(q: str, skip: int, limit: int):
    """辅助函数：搜索帖子"""
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
        ts_headline(p.title, plainto_tsquery('zhcfg', $1), 'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15') as highlighted_title,
        ts_headline(p.content, plainto_tsquery('zhcfg', $1), 'StartSel=<mark>, StopSel=</mark>, MaxWords=60, MinWords=30') as highlighted_content
    FROM posts p
    WHERE p.search_vector @@ plainto_tsquery('zhcfg', $1)
        AND p.deleted_at IS NULL
    ORDER BY rank DESC, p.created_at DESC
    LIMIT $2 OFFSET $3
    """

    count_sql = """
    SELECT COUNT(*) as total
    FROM posts p
    WHERE p.search_vector @@ plainto_tsquery('zhcfg', $1)
        AND p.deleted_at IS NULL
    """

    conn = connections.get("default")
    results = await conn.execute_query_dict(sql, [q, limit, skip])
    count_result = await conn.execute_query_dict(count_sql, [q])

    return {
        "results": results,
        "total": count_result[0]['total'] if count_result else 0
    }


async def _fetch_comments_search(q: str, skip: int, limit: int):
    """辅助函数：搜索评论"""
    sql = """
    SELECT
        c.id,
        c.content,
        c.post_id,
        c.author_id,
        c.score,
        c.upvotes,
        c.downvotes,
        c.created_at,
        c.updated_at,
        ts_rank(c.search_vector, plainto_tsquery('zhcfg', $1)) as rank,
        ts_headline(c.content, plainto_tsquery('zhcfg', $1), 'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15') as highlighted_content
    FROM comments c
    WHERE c.search_vector @@ plainto_tsquery('zhcfg', $1)
        AND c.deleted_at IS NULL
    ORDER BY rank DESC, c.created_at DESC
    LIMIT $2 OFFSET $3
    """

    count_sql = """
    SELECT COUNT(*) as total
    FROM comments c
    WHERE c.search_vector @@ plainto_tsquery('zhcfg', $1)
        AND c.deleted_at IS NULL
    """

    conn = connections.get("default")
    results = await conn.execute_query_dict(sql, [q, limit, skip])
    count_result = await conn.execute_query_dict(count_sql, [q])

    return {
        "results": results,
        "total": count_result[0]['total'] if count_result else 0
    }


async def _fetch_users_search(q: str, skip: int, limit: int):
    """辅助函数：搜索用户"""
    # 搜索活跃用户
    users = await User.filter(
        username__icontains=q
    ).filter(
        is_active=True
    ).all()

    # 同时搜索昵称
    users_by_nickname = await User.filter(
        nickname__icontains=q
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
            "is_superuser": u.is_superuser,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in paginated_users
    ]

    return {
        "results": results,
        "total": total
    }
