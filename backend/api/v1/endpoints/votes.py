"""
@Created on : 2025/12/8
@Author: wrn
@Des: 投票点赞路由
"""

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from tortoise.transactions import in_transaction
from tortoise.expressions import F
from models.user import User 
from core.cache import get_redis
from core.security import get_current_user
from schemas import vote as schemas
from models import post as models
from models.comment import Comment

router = APIRouter(tags=["投票点赞"])

@router.post("/vote", summary="统一投票接口（帖子/评论）")

async def vote(
    vote_in: schemas.VoteCreate,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    统一投票接口：支持帖子和评论
    1. 检查 DB 是否已投
    2. 计算分数差值
    3. 原子更新 DB score
    4. 更新 Redis 热度（仅帖子）
    """
    # 验证输入：必须提供 post_id 或 comment_id 之一
    if not vote_in.post_id and not vote_in.comment_id:
        raise HTTPException(status_code=400, detail="必须指定 post_id 或 comment_id")
    if vote_in.post_id and vote_in.comment_id:
        raise HTTPException(status_code=400, detail="不能同时为帖子和评论投票")

    # 确定投票目标
    if vote_in.post_id:
        target = await models.Post.get_or_none(id=vote_in.post_id)
        target_type = "post"
        if not target:
            raise HTTPException(status_code=404, detail="帖子不存在")
    else:  # comment_id
        target = await Comment.get_or_none(id=vote_in.comment_id)
        target_type = "comment"
        if not target:
            raise HTTPException(status_code=404, detail="评论不存在")

    # 开启事务保证数据一致性
    async with in_transaction():
        # 查询旧投票
        if target_type == "post":
            existing_vote = await models.Vote.filter(user=current_user, post=target).first()
        else:
            existing_vote = await models.Vote.filter(user=current_user, comment=target).first()

        score_delta = 0

        if existing_vote:
            if existing_vote.direction == vote_in.direction:
                # 重复点击同一方向 -> 取消投票
                score_delta = -existing_vote.direction
                await existing_vote.delete()
            else:
                # 改变方向 (踩变赞: -1 -> 1, delta = 2)
                score_delta = vote_in.direction - existing_vote.direction
                existing_vote.direction = vote_in.direction
                await existing_vote.save()
        else:
            # 新投票
            score_delta = vote_in.direction
            if target_type == "post":
                await models.Vote.create(user=current_user, post=target, direction=vote_in.direction)
            else:
                await models.Vote.create(user=current_user, comment=target, direction=vote_in.direction)

        # 数据库原子更新 (防止并发写错)
        if score_delta != 0:
            if target_type == "post":
                await models.Post.filter(id=target.id).update(score=F('score') + score_delta)
                # 重新计算 hot_rank
                await target.update_hot_rank()
            else:
                await Comment.filter(id=target.id).update(score=F('score') + score_delta)

    # Redis 更新 (仅帖子需要更新热度)
    if target_type == "post" and score_delta != 0:
        from core.redis_service import hot_rank_service

        # 确定投票类型
        vote_type = 'upvote' if score_delta > 0 else 'downvote'

        # 更新 Redis 交互计数和热度
        await hot_rank_service.increment_interaction(
            redis=redis,
            post_id=target.id,
            interaction_type=vote_type,
            created_at=target.created_at
        )

    return {
        "message": "投票成功",
        "target_type": target_type,
        "delta": score_delta
    }

@router.get("/comments/{comment_id}/vote", summary="获取评论投票状态")
async def get_comment_vote_status(
    comment_id: int,
    current_user: User = Depends(get_current_user),
):
    """获取用户对某评论的投票状态"""
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    vote = await models.Vote.filter(
        user=current_user,
        comment=comment
    ).first()

    return {
        "comment_id": comment_id,
        "user_vote": vote.direction if vote else 0,
        "score": comment.score
    }