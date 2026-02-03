"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from redis.asyncio import Redis
from backend.models.user import User
from backend.models.community import Community
from backend.core.security import get_current_user
from backend.core.permissions import can_post_in_community, can_moderate_post, require_superuser, get_community_moderator
from backend.core.audit import create_audit_log
from backend.core.cache import get_redis
from backend.models.audit_log import ActionType, TargetType
from backend.schemas import post as schemas
from backend.models import post as models

router = APIRouter(tags=["帖子相关"])


async def _get_paginated_posts(
    order_by: str,
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    include_deleted: bool = False,
):
    """
    通用的分页帖子查询函数

    Args:
        order_by: 排序字段，如 "-created_at" 或 "-hot_rank"
        community_id: 社区ID过滤
        skip: 跳过条数
        limit: 返回条数
        include_deleted: 是否包含已删除帖子
    """
    # 构建查询
    query = models.Post.all().order_by(order_by)

    # 预加载关联对象，避免 N+1 查询问题
    query = query.select_related('author', 'community')

    # 过滤软删除的帖子
    if not include_deleted:
        query = query.filter(deleted_at__isnull=True)

    if community_id:
        query = query.filter(community_id=community_id)

    # 获取总条数
    total = await query.count()

    # 获取当前页数据
    items = await query.offset(skip).limit(limit)

    # 计算是否有更多数据
    has_more = skip + limit < total

    return schemas.PaginatedPostResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )


@router.get("/posts", response_model=schemas.PaginatedPostResponse, summary="获取帖子列表")

async def list_posts(
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100), # 限制每页最多 100 条
    include_deleted: bool = False,
):
    """
    获取帖子列表（分页）

    返回分页信息，前端可根据 total 计算总页数
    """
    return await _get_paginated_posts(
        order_by="-created_at",
        community_id=community_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted
    )


@router.get("/posts/hot", response_model=schemas.PaginatedPostResponse, summary="获取热门帖子列表")

async def get_hot_posts(
    community_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100), # 限制每页最多 100 条
    redis: Redis = Depends(get_redis),
):
    """
    获取热门帖子列表（分页）

    使用 Redis ZSET 缓存热门帖子，避免频繁查询数据库
    """
    from backend.core.redis_service import hot_rank_service, post_cache_service

    # 1. 从 Redis ZSET 获取热门 post_ids
    post_ids = await hot_rank_service.get_hot_post_ids(
        redis=redis,
        limit=limit,
        offset=skip,
        community_id=community_id
    )

    if not post_ids:
        # Redis 没有数据，返回空结果
        return schemas.PaginatedPostResponse(
            items=[],
            total=0,
            skip=skip,
            limit=limit,
            has_more=False
        )

    # 2. 批量获取缓存详情
    cached_posts = await post_cache_service.get_cached_posts_batch(redis, post_ids)

    # 3. 找出缓存未命中的帖子
    missing_ids = [pid for pid in post_ids if pid not in cached_posts]

    # 4. 从数据库获取未缓存的帖子
    if missing_ids:
        db_posts = await models.Post.filter(
            id__in=missing_ids,
            deleted_at__isnull=True
        ).select_related('author', 'community')

        # 转换为字典并回填缓存
        for post in db_posts:
            post_dict = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "score": post.score,
                "hot_rank": post.hot_rank,
                "author_id": post.author_id,
                "community_id": post.community_id,
                "author": {
                    "id": post.author.id,
                    "username": post.author.username,
                } if post.author else None,
                "community": {
                    "id": post.community.id,
                    "name": post.community.name,
                } if post.community else None,
                "upvotes": post.upvotes,
                "downvotes": post.downvotes,
                "is_edited": post.is_edited,
                "is_locked": post.is_locked,
                "is_highlighted": post.is_highlighted,
                "is_pinned": post.is_pinned,
                "deleted_by_id": post.deleted_by_id,
                "deleted_at": post.deleted_at.isoformat() if post.deleted_at else None,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            }
            cached_posts[post.id] = post_dict
            # 异步回填缓存（不阻塞响应）
            await post_cache_service.cache_post(redis, post.id, post_dict)

    # 5. 按 post_ids 顺序排序（保持热度顺序）
    items = [cached_posts[pid] for pid in post_ids if pid in cached_posts]

    # 6. 计算总数和是否有更多数据
    # 这里简化处理，实际可以从 ZSET 获取总数
    total = await redis.zcard(
        hot_rank_service._get_hot_posts_key(community_id)
    )
    has_more = skip + limit < total

    return schemas.PaginatedPostResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

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
    # 重新获取帖子以预加载关联对象
    post = await models.Post.get(id=post.id).select_related('author', 'community')
    return post

@router.get("/posts/{post_id}", response_model=schemas.PostOut,summary="获取帖子详情")

async def get_post(
    post_id: int,
    redis: Redis = Depends(get_redis),
):
    """获取单个帖子详情"""
    from backend.core.redis_service import hot_rank_service

    post = await models.Post.get_or_none(id=post_id).select_related('author', 'community')
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 增加浏览计数并更新热度（异步执行，不阻塞响应）
    await hot_rank_service.increment_interaction(
        redis=redis,
        post_id=post_id,
        interaction_type='view',
        created_at=post.created_at
    )

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
        # 重新获取帖子，预加载关联对象
        post = await models.Post.get(id=post_id).select_related('author', 'community')

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
    from tortoise import transactions

    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 检查是否已删除
    if post.deleted_at:
        raise HTTPException(status_code=400, detail="帖子已被删除")

    # 权限检查：作者、版主或超级管理员可以删除
    is_author = post.author_id == current_user.id
    is_superuser = current_user.is_superuser

    # 如果不是作者也不是超级管理员，检查是否有版主权限
    is_moderator = False
    if not is_author and not is_superuser:
        _, membership = await can_moderate_post(post_id, current_user)
        is_moderator = membership is not None

    if not is_author and not is_moderator and not is_superuser:
        raise HTTPException(status_code=403, detail="无权删除此帖子")

    # 使用事务确保删除和审计日志的原子性
    async with transactions.in_transaction():
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

    # 从 Redis 热门榜中移除（异步执行，不阻塞响应）
    from backend.core.redis_service import hot_rank_service, post_cache_service
    redis_dep = get_redis()
    redis = await redis_dep.__anext__()
    try:
        await hot_rank_service.remove_post(
            redis=redis,
            post_id=post_id,
            community_id=post.community_id
        )
        await post_cache_service.invalidate_post(redis, post_id)
    finally:
        await redis.close()

    return {"message": "帖子删除成功"}

@router.post("/posts/{post_id}/restore", summary="恢复帖子")

async def restore_post(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(require_superuser),  # 改为只允许超级管理员
):
    """恢复已删除的帖子（仅超级管理员）"""
    from tortoise import transactions

    post = await models.Post.get_or_none(id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    if not post.deleted_at:
        raise HTTPException(status_code=400, detail="帖子未被删除")

    # 使用事务确保恢复和审计日志的原子性
    async with transactions.in_transaction():
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


async def _update_post_moderation(
    post_id: int,
    field_name: str,
    value: bool,
    action_true: ActionType,
    action_false: ActionType,
    success_message_true: str,
    success_message_false: str,
    permission_error: str,
    current_user: User,
    reason: Optional[str] = None,
):
    """
    通用的帖子管理更新函数

    Args:
        post_id: 帖子ID
        field_name: 要更新的字段名
        value: 更新的值
        action_true: 设置为 True 时的审计动作类型
        action_false: 设置为 False 时的审计动作类型
        success_message_true: 设置成功时的消息
        success_message_false: 取消成功时的消息
        permission_error: 权限错误提示
        current_user: 当前用户
        reason: 操作原因
    """
    from tortoise import transactions

    post, membership = await can_moderate_post(post_id, current_user)

    if not membership:
        raise HTTPException(status_code=403, detail=permission_error)

    action = action_true if value else action_false

    # 使用事务确保更新和审计日志的原子性
    async with transactions.in_transaction():
        await models.Post.filter(id=post_id).update(**{field_name: value})

        await create_audit_log(
            actor=current_user,
            target_type=TargetType.POST,
            target_id=post_id,
            action_type=action,
            reason=reason
        )

    return {"message": success_message_true if value else success_message_false}


@router.patch("/posts/{post_id}/lock", summary="锁定/解锁帖子")
async def lock_post(
    post_id: int,
    is_locked: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """锁定或解锁帖子（仅版主）"""
    return await _update_post_moderation(
        post_id=post_id,
        field_name="is_locked",
        value=is_locked,
        action_true=ActionType.LOCK_POST,
        action_false=ActionType.UNLOCK_POST,
        success_message_true="帖子已锁定",
        success_message_false="帖子已解锁",
        permission_error="仅版主可以锁定帖子",
        current_user=current_user,
        reason=reason
    )


@router.patch("/posts/{post_id}/highlight", summary="设为/取消精华")
async def highlight_post(
    post_id: int,
    is_highlighted: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """设置或取消精华（仅版主）"""
    return await _update_post_moderation(
        post_id=post_id,
        field_name="is_highlighted",
        value=is_highlighted,
        action_true=ActionType.HIGHLIGHT_POST,
        action_false=ActionType.UNHIGHLIGHT_POST,
        success_message_true="已设置精华",
        success_message_false="已取消精华",
        permission_error="仅版主可以设置精华",
        current_user=current_user,
        reason=reason
    )


@router.patch("/posts/{post_id}/pin", summary="置顶/取消置顶")
async def pin_post(
    post_id: int,
    is_pinned: bool,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """置顶或取消置顶帖子（仅版主）"""
    return await _update_post_moderation(
        post_id=post_id,
        field_name="is_pinned",
        value=is_pinned,
        action_true=ActionType.PIN_POST,
        action_false=ActionType.UNPIN_POST,
        success_message_true="帖子已置顶",
        success_message_false="帖子已取消置顶",
        permission_error="仅版主可以置顶帖子",
        current_user=current_user,
        reason=reason
    )

