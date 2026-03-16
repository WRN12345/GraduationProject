"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from redis.asyncio import Redis
from models.user import User
from core.security import get_current_user, get_current_user_optional
from core.permissions import can_post_in_community, require_superuser
from core.cache import get_redis
from schemas import post as schemas
from core.services import post_service

router = APIRouter(tags=["帖子相关"])


@router.get("/posts", response_model=schemas.PaginatedPostResponse, summary="获取帖子列表")
async def list_posts(
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    include_deleted: bool = False,
    current_user: Optional[User] = Depends(get_current_user_optional),
    redis: Redis = Depends(get_redis)
):
    """获取帖子列表（分页，包含用户状态）"""
    return await post_service.get_posts_list(
        redis=redis,
        order_by="-created_at",
        community_id=community_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
        current_user=current_user
    )


@router.get("/posts/hot", response_model=schemas.PaginatedPostResponse, summary="获取热门帖子列表")
async def get_hot_posts(
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    redis: Redis = Depends(get_redis),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取热门帖子列表（分页）"""
    return await post_service.get_hot_posts(
        redis=redis,
        community_id=community_id,
        skip=skip,
        limit=limit,
        current_user=current_user
    )


@router.post("/posts", response_model=schemas.PostOut, summary="创建新帖子")
async def create_post(
    post_in: schemas.PostCreate,
    current_user: User = Depends(get_current_user),
):
    """发布新帖"""
    # 验证用户是否可以在该社区发帖
    # can_post_in_community 会抛出 HTTPException，我们让它自然传播
    await can_post_in_community(post_in.community_id, current_user)

    result = await post_service.create_post(
        user=current_user,
        title=post_in.title,
        content=post_in.content,
        community_id=post_in.community_id,
        attachment_ids=post_in.attachment_ids
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/posts/{post_id}", response_model=schemas.PostOut, summary="获取帖子详情")
async def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    redis: Redis = Depends(get_redis),
):
    """获取单个帖子详情（包含用户状态）"""
    result = await post_service.get_post_detail(
        redis=redis,
        post_id=post_id,
        current_user=current_user
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.put("/posts/{post_id}", response_model=schemas.PostOut, summary="编辑帖子")
async def update_post(
    post_id: int,
    post_in: schemas.PostUpdate,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    """编辑帖子（仅作者）"""
    result = await post_service.update_post(
        redis=redis,
        post_id=post_id,
        user=current_user,
        title=post_in.title,
        content=post_in.content,
        attachment_ids=post_in.attachment_ids
    )

    if "error" in result:
        error_msg = result["error"]
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "无权" in error_msg:
            raise HTTPException(status_code=403, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return result


@router.patch("/posts/{post_id}", response_model=schemas.PostOut, summary="部分编辑帖子")
async def patch_post(
    post_id: int,
    post_in: schemas.PostUpdate,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    """部分编辑帖子（与 PUT 相同）"""
    return await update_post(post_id, post_in, current_user, redis)


@router.delete("/posts/{post_id}", summary="删除帖子")
async def delete_post(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """软删除帖子（作者或管理员）"""
    result = await post_service.delete_post(
        post_id=post_id,
        user=current_user,
        reason=reason
    )

    if "error" in result:
        error_msg = result["error"]
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "无权" in error_msg:
            raise HTTPException(status_code=403, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return result


@router.post("/posts/{post_id}/restore", summary="恢复帖子")
async def restore_post(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(require_superuser),
):
    """恢复已删除的帖子（仅超级管理员）"""
    result = await post_service.restore_post(
        post_id=post_id,
        user=current_user,
        reason=reason
    )

    if "error" in result:
        error_msg = result["error"]
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return result


# 帖子管理端点（需要版主权限）


@router.patch("/posts/{post_id}/lock", summary="锁定/解锁帖子")
async def lock_post(
    post_id: int,
    is_locked: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """锁定或解锁帖子（仅版主）"""
    result = await post_service.lock_post(
        post_id=post_id,
        is_locked=is_locked,
        user=current_user,
        reason=reason
    )

    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])

    return result


@router.patch("/posts/{post_id}/highlight", summary="设为/取消精华")
async def highlight_post(
    post_id: int,
    is_highlighted: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """设置或取消精华（仅版主）"""
    result = await post_service.highlight_post(
        post_id=post_id,
        is_highlighted=is_highlighted,
        user=current_user,
        reason=reason
    )

    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])

    return result


@router.patch("/posts/{post_id}/pin", summary="置顶/取消置顶")
async def pin_post(
    post_id: int,
    is_pinned: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """置顶或取消置顶帖子（仅版主）"""
    result = await post_service.pin_post(
        post_id=post_id,
        is_pinned=is_pinned,
        user=current_user,
        reason=reason
    )

    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])

    return result
