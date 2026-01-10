"""
@Created on : 2025/12/8
@Author: wrn
@Des: 社区板块
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.core.security import get_current_user
from backend.models.community import Community 
from backend.models.user import User
from backend.schemas.community import CommunityCreate, CommunityOut

router = APIRouter(tags=["社区板块"])

@router.get("/", response_model=List[CommunityOut],summary="获取社区列表")

async def read_communities(
    skip: int = 0, 
    limit: int = 20
):
    """
    获取社区列表
    """
    return await Community.all().offset(skip).limit(limit)

@router.post("/", response_model=CommunityOut, status_code=201,summary="创建新社区")

async def create_community(
    community_in: CommunityCreate,
    current_user: User = Depends(get_current_user),
):
    """
    创建一个新社区 
    """
    # 1. 检查同名社区是否存在
    if await Community.filter(name=community_in.name).exists():
        raise HTTPException(
            status_code=400,
            detail="Community with this name already exists",
        )

    # 2. 创建社区
    community = await Community.create(
        **community_in.model_dump(),
        creator=current_user # 关联当前登录用户
    )
    return community

@router.get("/{name}", response_model=CommunityOut, summary="根据名字获取社区详情")

async def read_community_by_name(name: str):
    """
    根据名字获取社区详情
    """
    community = await Community.get_or_none(name=name)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community