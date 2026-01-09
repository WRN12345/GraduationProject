"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
from backend.models.user import User
from backend.core.security import get_current_user
from backend.schemas import post as schemas
from backend.models import post as models

router = APIRouter(tags=["帖子相关"])


@router.get("/posts", response_model=List[schemas.PostOut], summary="获取帖子列表")

async def list_posts(
    community_id: int = None,
    skip: int = 0,
    limit: int = 20,
    include_deleted: bool = False,
):
    """获取帖子列表"""
    query = models.Post.all().order_by("-created_at")

    # 过滤软删除的帖子
    if not include_deleted:
        query = query.filter(deleted_at__isnull=True)

    if community_id:
        query = query.filter(community_id=community_id)
    return await query.offset(skip).limit(limit)

@router.post("/posts", response_model=schemas.PostOut, summary="创建新帖子")

async def create_post(
    post_in: schemas.PostCreate,
    current_user: User = Depends(get_current_user),
):
    """发布新帖"""
    # 校验板块是否存在
    if not await models.Community.exists(id=post_in.community_id):
        raise HTTPException(status_code=404, detail="Community not found")

    post = await models.Post.create(
        **post_in.model_dump(),
        author=current_user
    )
    return post

@router.get("/posts/{post_id}", response_model=schemas.PostOut,summary="获取帖子详情")

async def get_post(post_id: int):
    """获取单个帖子详情"""
    post = await models.Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return post

@router.put("/posts/{post_id}", response_model=schemas.PostOut, summary="编辑帖子" )

async def update_post(
    post_id: int,
    post_in: schemas.PostUpdate,
    current_user: User = Depends(get_current_user),
):
    """编辑帖子（仅作者）"""
    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 权限检查：只有作者可以编辑
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权编辑此帖子")

    # 检查是否已软删除
    if post.deleted_at:
        raise HTTPException(status_code=400, detail="无法编辑已删除的帖子")

    # 更新字段
    update_data = post_in.model_dump(exclude_unset=True)
    if update_data:
        await models.Post.filter(id=post_id).update(
            **update_data,
            is_edited=True
        )
        await post.refresh_from_db()

    return post

@router.patch("/posts/{post_id}", response_model=schemas.PostOut, summary="部分编辑帖子")

async def patch_post(
    post_id: int,
    post_in: schemas.PostUpdate,
    current_user: User = Depends(get_current_user),
):
    """部分编辑帖子（与 PUT 相同）"""
    return await update_post(post_id, post_in, current_user)

@router.delete("/posts/{post_id}", summary="删除帖子" )

async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
):
    """软删除帖子（作者或管理员）"""
    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 权限检查：作者或管理员
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除此帖子")

    # 软删除
    await models.Post.filter(id=post_id).update(
        deleted_at=datetime.now(timezone.utc)
    )

    return {"message": "帖子删除成功"}

@router.post("/posts/{post_id}/restore", summary="恢复帖子")

async def restore_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
):
    """恢复已删除的帖子"""
    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 权限检查：作者或管理员
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权恢复此帖子")

    await models.Post.filter(id=post_id).update(deleted_at=None)

    return {"message": "帖子恢复成功"}

@router.get("/posts/hot", response_model=List[schemas.PostOut], summary="获取热门帖子列表")

async def get_hot_posts(
    community_id: int = None,
    skip: int = 0,
    limit: int = 20,
):
    """
    获取热门帖子列表
    按 hot_rank 排序，hot_rank 考虑了分数和时间衰减
    """
    query = models.Post.all().order_by("-hot_rank")

    # 过滤软删除的帖子
    query = query.filter(deleted_at__isnull=True)

    if community_id:
        query = query.filter(community_id=community_id)

    return await query.offset(skip).limit(limit)
