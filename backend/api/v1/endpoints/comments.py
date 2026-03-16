"""
@Created on : 2025/12/8
@Author: wrn
@Des: 评论路由
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional
from models.user import User
from models.comment import Comment
from models.post import Post
from core.security import get_current_user
from core.permissions import can_comment_on_post, get_community_moderator
from core.audit import create_audit_log
from models.audit_log import ActionType, TargetType
from schemas import comment as schemas
from core.services import comment_service

router = APIRouter(tags=["评论相关"])


@router.post("/comments", response_model=schemas.CommentOut, summary="创建评论")
async def create_comment(
    comment_in: schemas.CommentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """创建评论并更新 Redis 缓存"""
    # 验证帖子存在且用户可以评论
    post = await can_comment_on_post(comment_in.post_id, current_user)

    redis = request.app.state.redis
    result = await comment_service.create_comment(
        redis=redis,
        post_id=comment_in.post_id,
        user=current_user,
        content=comment_in.content,
        parent_id=comment_in.parent_id
    )

    return result


@router.get("/posts/{post_id}/comments", summary="获取帖子评论树（懒加载）")
async def get_comments_tree(
    post_id: int,
    root_offset: int = Query(0, ge=0, description="根评论偏移量"),
    root_limit: int = Query(20, ge=1, le=100, description="根评论数量"),
    reply_limit: int = Query(3, ge=0, le=10, description="每个根评论预加载的子评论数"),
    request: Request = None
):
    """
    Redis 缓存优先的懒加载评论树

    - 首次加载：返回根评论 + 每个根评论的前 N 条子评论
    - 后续加载：通过 get_comment_replies 按需获取子评论
    - 缓存未命中：从数据库加载并重建缓存
    """
    redis = request.app.state.redis

    return await comment_service.get_comment_tree(
        redis=redis,
        post_id=post_id,
        root_offset=root_offset,
        root_limit=root_limit,
        reply_limit=reply_limit,
        include_children=True
    )


@router.get("/posts/{post_id}/comments/{parent_id}/replies", summary="获取子评论列表")
async def get_comment_replies(
    post_id: int,
    parent_id: int,
    offset: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    request: Request = None
):
    """
    按需加载子评论（点击展开时调用）

    - 返回指定父评论的子评论列表
    - 支持分页
    - 包含每条子评论的子评论数量统计
    """
    redis = request.app.state.redis

    return await comment_service.get_comment_replies(
        redis=redis,
        post_id=post_id,
        parent_id=parent_id,
        offset=offset,
        limit=limit
    )


@router.put("/comments/{comment_id}", response_model=schemas.CommentOut, summary="编辑评论")
async def update_comment(
    comment_id: int,
    comment_in: schemas.CommentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """编辑评论（仅作者）并失效缓存"""
    redis = request.app.state.redis
    result = await comment_service.update_comment(
        redis=redis,
        comment_id=comment_id,
        user=current_user,
        content=comment_in.content
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


@router.delete("/comments/{comment_id}", summary="删除评论")
async def delete_comment(
    comment_id: int,
    request: Request,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """软删除评论（作者或管理员）并失效缓存"""
    comment = await Comment.get_or_none(id=comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # 权限检查
    is_author = comment.author_id == current_user.id
    is_moderator = False

    if not is_author:
        # 检查是否为版主
        post = await Post.get(id=comment.post_id)
        try:
            await get_community_moderator(post.community_id, current_user)
            is_moderator = True
        except HTTPException:
            pass

    if not is_author and not is_moderator and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除此评论")

    redis = request.app.state.redis
    result = await comment_service.delete_comment(
        redis=redis,
        comment_id=comment_id,
        user=current_user,
        reason=reason,
        is_moderator=is_moderator
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.COMMENT,
        target_id=comment_id,
        action_type=ActionType.DELETE_COMMENT,
        reason=reason,
        metadata={"is_author": is_author, "is_moderator": is_moderator}
    )

    return result


@router.post("/comments/{comment_id}/restore", summary="恢复评论")
async def restore_comment(
    comment_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """恢复已删除的评论并失效缓存"""
    redis = request.app.state.redis
    result = await comment_service.restore_comment(
        redis=redis,
        comment_id=comment_id,
        user=current_user
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