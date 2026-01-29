"""
@Created on : 2025/12/8
@Author: wrn
@Des: 社区板块
"""
from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from backend.core.security import get_current_user
from backend.models.community import Community
from backend.models.user import User
from backend.schemas.community import CommunityCreate, CommunityOut, CommunityRecommendation

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
    限制：每个用户每月只能创建一个社区
    """
    # 1. 检查同名社区是否存在
    if await Community.filter(name=community_in.name).exists():
        raise HTTPException(
            status_code=400,
            detail="社区名称已存在",
        )

    # 2. 检查用户在过去30天内是否创建过社区
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_community = await Community.filter(
        creator=current_user,
        created_at__gte=thirty_days_ago
    ).first()

    if recent_community:
        # 计算还需要等待多少天
        days_remaining = 30 - (datetime.now(timezone.utc) - recent_community.created_at).days
        raise HTTPException(
            status_code=429,
            detail=f"您创建社区过于频繁，请等待 {days_remaining} 天后再试",
        )

    # 3. 创建社区
    community = await Community.create(
        **community_in.model_dump(),
        creator=current_user # 关联当前登录用户
    )
    return community

@router.get("/recommend", response_model=List[CommunityRecommendation], summary="根据帖子内容推荐社区")
async def recommend_communities(
    title: str,
    content: str = None,
    limit: int = 5,
):
    """
    根据帖子标题和内容推荐适合的社区
    使用简单的关键词匹配算法
    """
    # 获取所有社区
    all_communities = await Community.all()

    # 简单的关键词匹配算法
    recommendations = []

    # 提取关键词（去除标点符号，分割成词）
    import re
    def extract_keywords(text):
        if not text:
            return []
        # 简单分词（按空格和常见标点分割）
        words = re.findall(r'[\w]+', text.lower())
        # 过滤掉常见的停用词
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', '的', '了', '是', '在', '和', '与', '或', '但是', '如果', '那么', '因为', '所以', '这个', '那个'}
        return [w for w in words if len(w) > 1 and w not in stopwords]

    title_keywords = extract_keywords(title)
    content_keywords = extract_keywords(content) if content else []
    all_keywords = set(title_keywords + content_keywords)

    # 为每个社区计算匹配分数
    for community in all_communities:
        score = 0

        # 检查社区名称匹配
        community_keywords = extract_keywords(community.name)
        for keyword in all_keywords:
            if keyword in community_keywords:
                score += 3  # 名称匹配权重高

        # 检查描述匹配
        if community.description:
            desc_keywords = extract_keywords(community.description)
            for keyword in all_keywords:
                if keyword in desc_keywords:
                    score += 1  # 描述匹配权重低

        # 根据成员数量给予额外分数（热门社区优先）
        score += min(community.member_count / 10, 5)

        if score > 0:
            recommendations.append((community, score))

    # 按分数排序并返回前N个
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # 构建返回结果
    result = []
    for community, score in recommendations[:limit]:
        result.append(CommunityRecommendation(
            id=community.id,
            name=community.name,
            description=community.description,
            member_count=community.member_count,
            match_score=round(score, 2)
        ))

    return result

@router.get("/{name}", response_model=CommunityOut, summary="根据名字获取社区详情")

async def read_community_by_name(name: str):
    """
    根据名字获取社区详情
    """
    community = await Community.get_or_none(name=name)
    if not community:
        raise HTTPException(status_code=404, detail="社区不存在")
    return community