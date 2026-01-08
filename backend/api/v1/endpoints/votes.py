"""
@Created on : 2025/12/8
@Author: wrn
@Des: 投票点赞路由
"""

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from tortoise.transactions import in_transaction
from tortoise.expressions import F
from backend.models.user import User 
from backend.core.cache import get_redis
from backend.core.security import get_current_user
from backend.schemas import vote as schemas
from backend.models import post as models

router = APIRouter()

@router.post("/vote")

async def vote_post(
    vote_in: schemas.VoteCreate,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    投票逻辑：
    1. 检查 DB 是否已投
    2. 计算分数差值
    3. 原子更新 DB score
    4. 更新 Redis 热度
    """
    post = await models.Post.get_or_none(id=vote_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 开启事务保证数据一致性
    async with in_transaction():
        # 查询旧投票
        existing_vote = await models.Vote.filter(user=current_user, post=post).first()
        
        score_delta = 0
        
        if existing_vote:
            if existing_vote.value == vote_in.dir:
                # 重复点击同一方向 -> 取消投票
                score_delta = -existing_vote.value
                await existing_vote.delete()
            else:
                # 改变方向 (踩变赞: -1 -> 1, delta = 2)
                score_delta = vote_in.dir - existing_vote.value
                existing_vote.value = vote_in.dir
                await existing_vote.save()
        else:
            # 新投票
            score_delta = vote_in.dir
            await models.Vote.create(user=current_user, post=post, value=vote_in.dir)

        # 数据库原子更新 (防止并发写错)
        # post.score = post.score + score_delta
        if score_delta != 0:
            await models.Post.filter(id=post.id).update(score=F('score') + score_delta)

    # Redis 更新 (不需要事务，仅仅是缓存)
    # 维护一个有序集合做热榜: ZINCRBY hot_posts <delta> <post_id>
    if score_delta != 0:
        await redis.zincrby("global:hot_posts", score_delta, str(post.id))

    return {"msg": "Vote processed", "delta": score_delta}