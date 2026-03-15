"""
@Created on : 2026.3.13
@Author: wrn
@Des: 收藏管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from models.user import User
from models.post import Post
from core.cache import get_redis
from core.security import get_current_user
from services.bookmark_service import bookmark_service
from schemas import bookmark as bookmark_schemas
from schemas import post as post_schemas

router = APIRouter(tags=["收藏管理"])


@router.post("/bookmarks", summary="收藏帖子")
async def add_bookmark(
    bookmark_in: bookmark_schemas.BookmarkCreate,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """收藏指定帖子"""
    print(f"[DEBUG] 收藏请求: user_id={current_user.id}, post_id={bookmark_in.post_id}")

    # 预加载 author 和 community 关系
    post = await Post.filter(id=bookmark_in.post_id).select_related('author', 'community').first()
    if not post:
        print(f"[DEBUG] 帖子不存在: post_id={bookmark_in.post_id}")
        raise HTTPException(status_code=404, detail="帖子不存在")

    result = await bookmark_service.add_bookmark(
        redis=redis,
        user=current_user,
        post=post,
        folder=bookmark_in.folder,
        note=bookmark_in.note
    )

    print(f"[DEBUG] 收藏结果: {result}")

    if "error" in result:
        print(f"[DEBUG] 收藏失败: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.delete("/bookmarks/{post_id}", summary="取消收藏")
async def remove_bookmark(
    post_id: int,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """取消收藏指定帖子"""
    result = await bookmark_service.remove_bookmark(
        redis=redis,
        user=current_user,
        post_id=post_id
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/bookmarks", response_model=bookmark_schemas.BookmarkListResponse, summary="获取收藏列表")
async def get_bookmarks(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """获取当前用户的收藏列表（分页）"""
    return await bookmark_service.get_user_bookmarks(
        redis=redis,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/bookmarks/my-posts", response_model=post_schemas.PaginatedPostResponse, summary="获取我收藏的帖子")
async def get_my_bookmarked_posts(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    获取当前用户收藏的帖子列表（完整格式）

    返回完整的 PostOut 格式，可直接用于帖子列表组件渲染
    按收藏时间倒序排列
    """
    return await bookmark_service.get_user_bookmarked_posts(
        redis=redis,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        current_user=current_user
    )


@router.get("/bookmarks/check/{post_id}", summary="检查是否已收藏")
async def check_bookmarked(
    post_id: int,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """检查是否已收藏指定帖子"""
    bookmarked = await bookmark_service.is_bookmarked(
        redis=redis,
        user_id=current_user.id,
        post_id=post_id
    )

    return {
        "post_id": post_id,
        "bookmarked": bookmarked
    }


@router.post("/bookmarks/check-batch", summary="批量检查收藏状态")
async def check_batch_bookmarked(
    request: bookmark_schemas.BookmarkCheckRequest,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    批量检查多个帖子的收藏状态
    用于帖子列表页面
    """
    bookmarked = await bookmark_service.batch_check_bookmarked(
        redis=redis,
        user_id=current_user.id,
        post_ids=request.post_ids
    )

    return {
        "bookmarked": bookmarked
    }


@router.get("/posts/{post_id}/bookmark-count", summary="获取帖子收藏数")
async def get_bookmark_count(
    post_id: int,
    redis: Redis = Depends(get_redis)
):
    """获取帖子的收藏总数（公开接口）"""
    count = await bookmark_service.get_bookmark_count(
        redis=redis,
        post_id=post_id
    )

    return {
        "post_id": post_id,
        "bookmark_count": count
    }
