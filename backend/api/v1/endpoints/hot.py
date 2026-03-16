"""
@Created on : 2026.3.16
@Author: wrn
@Des: 热门内容相关 API 端点
"""
from typing import Optional
from fastapi import APIRouter, Query, Depends

from core.security import get_current_user_optional
from models.user import User
from core.services.content.hot_content_service import hot_content_service
from core.cache import get_redis
from schemas import hot as schemas

router = APIRouter(tags=["热门内容"])


@router.get(
    "/sidebar",
    response_model=schemas.SidebarHotResponse,
    summary="获取侧边栏热门内容",
    description="聚合返回热门帖子、热门社区、活跃用户的组合数据"
)
async def get_sidebar_hot_content(
    limit: int = Query(
        10,
        ge=5,
        le=20,
        description="每类内容返回数量（5-20条）"
    ),
    community_id: Optional[int] = Query(
        None,
        description="社区ID（可选，用于获取特定社区的热门帖子）"
    ),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取侧边栏热门内容

    返回：
    - hot_posts: 热门帖子列表
    - hot_communities: 热门社区列表
    - hot_users: 活跃用户列表

    说明：
    - 默认每类返回10条数据
    - 可通过 limit 参数调整（5-20条）
    - 可选传入 community_id 获取特定社区的热门帖子
    """
    redis = await get_redis().__anext__()

    try:
        result = await hot_content_service.get_sidebar_hot_content(
            redis=redis,
            limit=limit,
            community_id=community_id
        )
        return result
    finally:
        await redis.close()


__all__ = ["router"]
