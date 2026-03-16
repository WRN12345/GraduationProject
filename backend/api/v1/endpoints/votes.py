"""
@Created on : 2025/12/8
@Author: wrn
@Des: 投票点赞路由 - Redis 版
"""

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from models.user import User
from models.post import Post
from models.comment import Comment
from core.cache import get_redis
from core.security import get_current_user
from core.services import vote_service
from schemas import vote as schemas

router = APIRouter(tags=["投票点赞"])


@router.post("/vote", summary="统一投票接口（帖子/评论）- Redis版")
async def vote(
    vote_in: schemas.VoteCreate,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    统一投票接口：支持帖子和评论
    - 直接操作 Redis，立即返回
    - 定时任务异步同步到数据库
    - 支持点赞、点踩、取消
    """
    # 验证输入
    if not vote_in.post_id and not vote_in.comment_id:
        raise HTTPException(status_code=400, detail="必须指定 post_id 或 comment_id")
    if vote_in.post_id and vote_in.comment_id:
        raise HTTPException(status_code=400, detail="不能同时为帖子和评论投票")

    # 确定投票目标
    if vote_in.post_id:
        target = await Post.get_or_none(id=vote_in.post_id)
        target_type = "post"
        if not target:
            raise HTTPException(status_code=404, detail="帖子不存在")
        target_id = target.id
        target_created_at = target.created_at
    else:
        target = await Comment.get_or_none(id=vote_in.comment_id)
        target_type = "comment"
        if not target:
            raise HTTPException(status_code=404, detail="评论不存在")
        target_id = target.id
        target_created_at = None

    # 执行投票
    result = await vote_service.vote(
        redis=redis,
        user=current_user,
        target_type=target_type,
        target_id=target_id,
        direction=vote_in.direction,
        target_created_at=target_created_at
    )

    return {
        "target_type": target_type,
        "target_id": target_id,
        **result
    }


@router.get("/posts/{post_id}/vote", summary="获取帖子投票状态")
async def get_post_vote_status(
    post_id: int,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """获取用户对帖子的投票状态"""
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    status = await vote_service.get_user_vote_status(
        redis, current_user.id, 'post', post_id
    )

    upvotes, downvotes, score = await vote_service.get_vote_counts(
        redis, 'post', post_id
    )

    return {
        "post_id": post_id,
        "user_vote": status,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "score": score
    }


@router.get("/comments/{comment_id}/vote", summary="获取评论投票状态")
async def get_comment_vote_status(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """获取用户对评论的投票状态"""
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    status = await vote_service.get_user_vote_status(
        redis, current_user.id, 'comment', comment_id
    )

    upvotes, downvotes, score = await vote_service.get_vote_counts(
        redis, 'comment', comment_id
    )

    return {
        "comment_id": comment_id,
        "user_vote": status,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "score": score
    }


@router.post("/votes/batch-status", summary="批量获取投票状态")
async def get_batch_vote_status(
    request: schemas.BatchVoteStatusRequest,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    批量获取多个帖子/评论的投票状态
    用于帖子列表/评论列表页面
    """
    items = []
    for item in request.items:
        items.append((item.target_type, item.target_id))

    statuses = await vote_service.batch_get_vote_statuses(
        redis, current_user.id, items
    )

    return {
        "statuses": [
            {
                "target_type": target_type,
                "target_id": target_id,
                "user_vote": statuses.get((target_type, target_id), 0)
            }
            for target_type, target_id in items
        ]
    }
