"""
@Created on : 2026/3/15
@Author: wrn
@Des: 社区服务 - 社区管理 + 推荐
"""
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from models.community import Community
from models.user import User
from models.membership import CommunityMembership, MembershipRole
from schemas.community import CommunityCreate, CommunityOut, CommunityRecommendation
import re

import logging

logger = logging.getLogger(__name__)


class CommunityService:
    """社区服务 - 社区管理 + 推荐"""

    async def get_communities_list(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[Community]:
        """获取社区列表"""
        return await Community.all().offset(skip).limit(limit)

    async def create_community(
        self,
        user: User,
        name: str,
        description: Optional[str] = None
    ) -> Community:
        """
        创建社区

        Args:
            user: 当前用户
            name: 社区名称
            description: 社区描述

        Returns:
            Community: 创建的社区

        Raises:
            Returns {"error": "..."} on failure
        """
        # 1. 检查同名社区是否存在
        if await Community.filter(name=name).exists():
            return {"error": "社区名称已存在"}

        # 2. 检查用户在过去30天内是否创建过社区
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_community = await Community.filter(
            creator=user,
            created_at__gte=thirty_days_ago
        ).first()

        if recent_community:
            days_remaining = 30 - (datetime.now(timezone.utc) - recent_community.created_at).days
            return {"error": f"您创建社区过于频繁，请等待 {days_remaining} 天后再试"}

        # 3. 创建社区
        community = await Community.create(
            name=name,
            description=description,
            creator=user,
            member_count=1  # 创建者自动加入，所以初始成员数为1
        )

        # 4. 自动将创建者加入为群主
        await CommunityMembership.create(
            user=user,
            community=community,
            role=MembershipRole.OWNER.value
        )

        return community

    async def get_community_by_name(
        self,
        name: str
    ) -> Optional[Community]:
        """
        根据名称获取社区

        Args:
            name: 社区名称

        Returns:
            Optional[Community]: 社区对象

        Raises:
            Returns {"error": "..."} on failure
        """
        community = await Community.get_or_none(name=name)
        if not community:
            return {"error": "社区不存在"}
        return community

    async def get_community_by_id(
        self,
        community_id: int
    ) -> Optional[Community]:
        """
        根据ID获取社区

        Args:
            community_id: 社区ID

        Returns:
            Optional[Community]: 社区对象

        Raises:
            Returns {"error": "..."} on failure
        """
        from models.post import Post
        from models.membership import CommunityMembership

        community = await Community.get_or_none(id=community_id)
        if not community:
            return {"error": "社区不存在"}

        # 如果 post_count 为 0 或 member_count 为 0，动态计算并更新
        if community.post_count == 0 or community.member_count == 0:
            # 计算实际帖子数量
            actual_post_count = await Post.filter(
                community_id=community_id,
                deleted_at=None
            ).count()

            # 计算实际成员数量
            actual_member_count = await CommunityMembership.filter(
                community_id=community_id
            ).count()

            # 更新数据库
            await Community.filter(id=community_id).update(
                post_count=actual_post_count,
                member_count=actual_member_count
            )

            # 重新获取更新后的数据
            community = await Community.get_or_none(id=community_id)

        return community

    async def recommend_communities(
        self,
        title: str,
        content: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        推荐社区（关键词匹配）

        Args:
            title: 帖子标题
            content: 帖子内容
            limit: 返回数量

        Returns:
            List[dict]: 推荐的社区列表
        """
        # 获取所有社区（限制数量，避免全表扫描）
        all_communities = await Community.all().limit(200)

        def extract_keywords(text):
            if not text:
                return []
            words = re.findall(r'[\w]+', text.lower())
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', '的', '了', '是', '在', '和', '与', '或', '但是', '如果', '那么', '因为', '所以', '这个', '那个'}
            return [w for w in words if len(w) > 1 and w not in stopwords]

        title_keywords = extract_keywords(title)
        content_keywords = extract_keywords(content) if content else []
        all_keywords = set(title_keywords + content_keywords)

        # 为每个社区计算匹配分数
        recommendations = []
        for community in all_communities:
            score = 0

            # 检查社区名称匹配
            community_keywords = extract_keywords(community.name)
            for keyword in all_keywords:
                if keyword in community_keywords:
                    score += 3

            # 检查描述匹配
            if community.description:
                desc_keywords = extract_keywords(community.description)
                for keyword in all_keywords:
                    if keyword in desc_keywords:
                        score += 1

            # 根据成员数量给予额外分数
            score += min(community.member_count / 10, 5)

            if score > 0:
                recommendations.append((community, score))

        # 按分数排序并返回前N个
        recommendations.sort(key=lambda x: x[1], reverse=True)

        # 构建返回结果
        result = []
        for community, score in recommendations[:limit]:
            result.append({
                "id": community.id,
                "name": community.name,
                "description": community.description,
                "member_count": community.member_count,
                "match_score": round(score, 2)
            })

        return result


# 导出服务实例
community_service = CommunityService()

__all__ = ["CommunityService", "community_service"]
