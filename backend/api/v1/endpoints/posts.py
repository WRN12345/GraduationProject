"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.models.user import User 
from backend.core.security import get_current_user
from backend.schemas import post as schemas
from backend.models import post as models

router = APIRouter()


@router.get("/posts", response_model=List[schemas.PostOut])

async def list_posts(
    community_id: int = None,
    skip: int = 0,
    limit: int = 20,
):
    """获取帖子列表"""
    query = models.Post.all().order_by("-created_at")
    if community_id:
        query = query.filter(community_id=community_id)
    return await query.offset(skip).limit(limit)

@router.post("/posts", response_model=schemas.PostOut)

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
