"""
@Created on : 2025/12/8
@Author: wrn
@Des: 社区板块
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from core.security import get_current_user
from models.user import User
from models.membership import CommunityMembership, MembershipRole
from schemas.community import CommunityCreate, CommunityOut, CommunityRecommendation
from core.services import community_service

router = APIRouter(prefix="/communities", tags=["社区板块"])

@router.get("/", response_model=List[CommunityOut], summary="获取社区列表")
async def read_communities(
    skip: int = 0,
    limit: int = 20
):
    """获取社区列表"""
    return await community_service.get_communities_list(skip=skip, limit=limit)

@router.post("/", response_model=CommunityOut, status_code=201, summary="创建新社区")
async def create_community(
    community_in: CommunityCreate,
    current_user: User = Depends(get_current_user),
):
    """创建一个新社区"""
    result = await community_service.create_community(
        user=current_user,
        name=community_in.name,
        description=community_in.description
    )

    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"]
        if "已存在" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=429, detail=error_msg)

    return result

@router.post("/{community_id}/join", summary="加入社区")
async def join_community(
    community_id: int,
    current_user: User = Depends(get_current_user),
):
    """加入指定社区"""
    from core.services import membership_service

    result = await membership_service.join_community(current_user, community_id)

    if "error" in result:
        error_msg = result["error"]
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return {"message": "成功加入社区"}

@router.get("/recommend", response_model=List[CommunityRecommendation], summary="根据帖子内容推荐社区")
async def recommend_communities(
    title: str,
    content: str = None,
    limit: int = 5,
):
    """根据帖子标题和内容推荐适合的社区"""
    return await community_service.recommend_communities(
        title=title,
        content=content,
        limit=limit
    )

@router.get("/{name}", response_model=CommunityOut, summary="根据名字获取社区详情")
async def read_community_by_name(name: str):
    """根据名字获取社区详情"""
    result = await community_service.get_community_by_name(name)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@router.get("/id/{community_id}", response_model=CommunityOut, summary="根据ID获取社区详情")
async def read_community_by_id(community_id: int):
    """根据ID获取社区详情"""
    result = await community_service.get_community_by_id(community_id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
