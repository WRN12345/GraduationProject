"""
@Created on : 2025/12/8
@Author: wrn
@Des: 全文搜索路由（使用 PostgreSQL 全文搜索）
"""

from fastapi import APIRouter, Query
from typing import Optional
import asyncio
from models.user import User
from schemas import search as search_schemas
from core.services import search_service

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
    return await search_service.search_posts(q, community_id, skip, limit)


@router.get("/search/users", summary="搜索用户")
async def search_users(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = 0,
    limit: int = 20,
):
    """搜索用户（用户名或昵称）"""
    return await search_service.search_users(q, skip, limit)


@router.get("/search", summary="搜索建议（快速预览）")
async def search_suggestions(
    q: str = Query(..., min_length=1, description="搜索关键词"),
):
    """搜索建议接口 - 返回帖子、用户的前 3 条匹配结果"""
    if not q or len(q.strip()) < 1:
        return {
            "posts": [],
            "users": [],
            "query": q.strip()
        }

    # 并发搜索各个类型（每个只取前 3 条）
    posts_task = search_service.search_posts(q, 0, 3)
    users_task = search_service.search_users(q, 0, 3)

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
    """全文搜索评论内容"""
    return await search_service.search_comments(q, skip, limit)


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
        "query": query,
        "totals": {
            "posts": posts_result.get("total", 0),
            "comments": comments_result.get("total", 0),
            "users": users_result.get("total", 0)
        }
    }


# 辅助函数（保留以支持统一搜索）
async def _fetch_posts_search(q: str, skip: int, limit: int):
    """辅助函数：搜索帖子（使用 SearchService）"""
    return await search_service.search_posts(q, None, skip, limit)


async def _fetch_comments_search(q: str, skip: int, limit: int):
    """辅助函数：搜索评论（使用 SearchService）"""
    return await search_service.search_comments(q, skip, limit)


async def _fetch_users_search(q: str, skip: int, limit: int):
    """辅助函数：搜索用户（使用 SearchService）"""
    return await search_service.search_users(q, skip, limit)
