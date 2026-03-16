"""
@Created on : 2026.3.16
@Author: wrn
@Des: 热门内容相关 Schema 定义
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class HotPostSchema(BaseModel):
    """热门帖子 Schema"""
    id: int
    title: str = Field(..., description="帖子标题")
    score: int = Field(..., description="投票分数")
    hot_rank: float = Field(..., description="热度分数")
    community_name: str = Field(..., description="社区名称")
    author_username: str = Field(..., description="作者用户名")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class HotCommunitySchema(BaseModel):
    """热门社区 Schema"""
    id: int
    name: str = Field(..., description="社区名称")
    description: str = Field(..., description="社区描述")
    member_count: int = Field(..., description="成员数量")
    post_count: int = Field(..., description="帖子数量")
    hot_rank: float = Field(..., description="热度分数")

    class Config:
        from_attributes = True


class HotUserSchema(BaseModel):
    """活跃用户 Schema"""
    id: int
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    karma: int = Field(..., description="声望值")
    post_count: int = Field(..., description="发帖数量")
    comment_count: int = Field(..., description="评论数量")
    hot_rank: float = Field(..., description="活跃度分数")

    class Config:
        from_attributes = True


class SidebarHotResponse(BaseModel):
    """侧边栏热门内容响应 Schema"""
    hot_posts: List[HotPostSchema] = Field(..., description="热门帖子列表")
    hot_communities: List[HotCommunitySchema] = Field(..., description="热门社区列表")
    hot_users: List[HotUserSchema] = Field(..., description="活跃用户列表")

    class Config:
        from_attributes = True


__all__ = [
    "HotPostSchema",
    "HotCommunitySchema",
    "HotUserSchema",
    "SidebarHotResponse",
]
