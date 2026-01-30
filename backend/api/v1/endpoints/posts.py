"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from backend.models.user import User
from backend.models.community import Community
from backend.core.security import get_current_user
from backend.core.permissions import can_post_in_community, can_moderate_post, require_superuser, get_community_moderator
from backend.core.audit import create_audit_log
from backend.models.audit_log import ActionType, TargetType
from backend.schemas import post as schemas
from backend.models import post as models

router = APIRouter(tags=["帖子相关"])


@router.get("/posts", response_model=List[schemas.PostOut], summary="获取帖子列表")

async def list_posts(
    community_id: Optional[int] = None,
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

@router.get("/posts/hot", response_model=List[schemas.PostOut], summary="获取热门帖子列表")

async def get_hot_posts(
    community_id: Optional[int] = None,
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

@router.post("/posts", response_model=schemas.PostOut, summary="创建新帖子")

async def create_post(
    post_in: schemas.PostCreate,
    current_user: User = Depends(get_current_user),
):
    """发布新帖"""
    # 校验板块是否存在
    if not await Community.exists(id=post_in.community_id):
        raise HTTPException(status_code=404, detail="社区不存在")

    # 验证用户是否可以在该社区发帖
    await can_post_in_community(post_in.community_id, current_user)

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

@router.delete("/posts/{post_id}", summary="删除帖子")

async def delete_post(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """软删除帖子（作者或管理员）"""
    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 权限检查
    is_author = post.author_id == current_user.id
    is_moderator = False

    if not is_author:
        # 检查是否为版主
        try:
            await get_community_moderator(post.community_id, current_user)
            is_moderator = True
        except HTTPException:
            pass

    if not is_author and not is_moderator and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除此帖子")

    # 软删除并记录删除者
    await models.Post.filter(id=post_id).update(
        deleted_at=datetime.now(timezone.utc),
        deleted_by=current_user.id
    )

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.POST,
        target_id=post_id,
        action_type=ActionType.DELETE_POST,
        reason=reason,
        metadata={"is_author": is_author, "is_moderator": is_moderator}
    )

    return {"message": "帖子删除成功"}

@router.post("/posts/{post_id}/restore", summary="恢复帖子")

async def restore_post(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(require_superuser),  # 改为只允许超级管理员
):
    """恢复已删除的帖子（仅超级管理员）"""
    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    if not post.deleted_at:
        raise HTTPException(status_code=400, detail="帖子未被删除")

    await models.Post.filter(id=post_id).update(
        deleted_at=None,
        deleted_by=None
    )

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.POST,
        target_id=post_id,
        action_type=ActionType.RESTORE_POST,
        reason=reason
    )

    return {"message": "帖子恢复成功"}


# 帖子管理端点（需要版主权限）


class PostModerationUpdate(BaseModel):
    """帖子管理更新"""
    is_locked: Optional[bool] = None
    is_highlighted: Optional[bool] = None
    is_pinned: Optional[bool] = None
    reason: Optional[str] = None


@router.patch("/posts/{post_id}/lock", summary="锁定/解锁帖子")
async def lock_post(
    post_id: int,
    is_locked: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """锁定或解锁帖子（仅版主）"""
    post, membership = await can_moderate_post(post_id, current_user)

    if not membership:
        raise HTTPException(status_code=403, detail="仅版主可以锁定帖子")

    await models.Post.filter(id=post_id).update(is_locked=is_locked)

    # 记录审计日志
    action = ActionType.LOCK_POST if is_locked else ActionType.UNLOCK_POST
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.POST,
        target_id=post_id,
        action_type=action,
        reason=reason
    )

    return {"message": f"帖子已{'锁定' if is_locked else '解锁'}"}


@router.patch("/posts/{post_id}/highlight", summary="设为/取消精华")
async def highlight_post(
    post_id: int,
    is_highlighted: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """设置或取消精华（仅版主）"""
    post, membership = await can_moderate_post(post_id, current_user)

    if not membership:
        raise HTTPException(status_code=403, detail="仅版主可以设置精华")

    await models.Post.filter(id=post_id).update(is_highlighted=is_highlighted)

    action = ActionType.HIGHLIGHT_POST if is_highlighted else ActionType.UNHIGHLIGHT_POST
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.POST,
        target_id=post_id,
        action_type=action,
        reason=reason
    )

    return {"message": f"已{'设置' if is_highlighted else '取消'}精华"}


@router.patch("/posts/{post_id}/pin", summary="置顶/取消置顶")
async def pin_post(
    post_id: int,
    is_pinned: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """置顶或取消置顶帖子（仅版主）"""
    post, membership = await can_moderate_post(post_id, current_user)

    if not membership:
        raise HTTPException(status_code=403, detail="仅版主可以置顶帖子")

    await models.Post.filter(id=post_id).update(is_pinned=is_pinned)

    action = ActionType.PIN_POST if is_pinned else ActionType.UNPIN_POST
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.POST,
        target_id=post_id,
        action_type=action,
        reason=reason
    )

    return {"message": f"帖子已{'置顶' if is_pinned else '取消置顶'}"}

