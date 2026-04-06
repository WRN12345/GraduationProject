"""
@Created on : 2026/4/3
@Author: wrn
@Des: 超级管理员相关 Schema
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- 控制面板统计数据 ---
class DashboardStats(BaseModel):
    """控制面板统计数据"""
    # 总量统计
    total_users: int = Field(description="总用户数")
    total_posts: int = Field(description="总帖子数")
    total_comments: int = Field(description="总评论数")
    total_communities: int = Field(description="总社区数")

    # 今日新增
    today_new_users: int = Field(default=0, description="今日新增用户数")
    today_new_posts: int = Field(default=0, description="今日新增帖子数")
    today_new_comments: int = Field(default=0, description="今日新增评论数")

    # 管理统计
    deleted_posts: int = Field(default=0, description="已软删除帖子数")
    deleted_comments: int = Field(default=0, description="已软删除评论数")
    hard_deleted_posts: int = Field(default=0, description="已硬删除帖子数")
    hard_deleted_comments: int = Field(default=0, description="已硬删除评论数")
    admin_users: int = Field(default=0, description="管理员用户数")
    banned_users: int = Field(default=0, description="已冻结用户数")


# --- 管理员审计日志输出 ---
class AdminAuditLogOut(BaseModel):
    """管理员审计日志输出"""
    id: int
    actor_id: int = Field(description="操作者ID")
    actor_name: Optional[str] = Field(default=None, description="操作者用户名")
    target_type: int = Field(description="目标类型")
    target_id: int = Field(description="目标ID")
    action_type: int = Field(description="操作类型")
    reason: Optional[str] = Field(default=None, description="操作原因")
    metadata: Any = Field(default={}, description="额外信息")
    created_at: datetime = Field(description="操作时间")

    model_config = ConfigDict(from_attributes=True)


# --- 管理员视角帖子作者信息 ---
class AdminPostAuthor(BaseModel):
    """管理员视角帖子作者信息"""
    id: int
    username: str
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- 管理员视角帖子社区信息 ---
class AdminPostCommunity(BaseModel):
    """管理员视角帖子社区信息"""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# --- 管理员视角的帖子信息 ---
class AdminPostOut(BaseModel):
    """管理员视角的帖子信息（包含作者信息、是否已删除等）"""
    id: int
    title: str
    content: Optional[str] = None
    community_id: int
    author_id: int
    author: Optional[AdminPostAuthor] = None
    community: Optional[AdminPostCommunity] = None
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    hot_rank: float = 0.0
    is_locked: bool = False
    is_highlighted: bool = False
    is_pinned: bool = False
    is_edited: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    comment_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# --- 管理员视角帖子详情（用于单个帖子）---
class AdminPostDetailOut(AdminPostOut):
    """管理员视角帖子详情（包含更多详情字段如附件等）"""
    attachments: Optional[List[dict]] = None

    model_config = ConfigDict(from_attributes=True)


# --- 管理员视角评论作者信息 ---
class AdminCommentAuthor(BaseModel):
    """管理员视角评论作者信息"""
    id: int
    username: str
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- 管理员视角的评论信息 ---
class AdminCommentOut(BaseModel):
    """管理员视角的评论信息"""
    id: int
    content: str
    post_id: int
    author_id: int
    author: Optional[AdminCommentAuthor] = None
    parent_id: Optional[int] = None
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    is_edited: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- 管理员操作响应 ---
class AdminActionResponse(BaseModel):
    """管理员操作响应"""
    message: str = Field(description="操作结果消息")
    target_id: int = Field(description="目标对象ID")


# --- 管理员用户列表输出 ---
class AdminUserOut(BaseModel):
    """管理员视角用户信息"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    karma: int = 0
    post_count: int = 0
    comment_count: int = 0
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- 管理员用户详情输出 ---
class AdminUserDetailOut(BaseModel):
    """管理员视角用户详细信息"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    karma: int = 0
    bio: Optional[str] = None
    post_count: int = 0
    comment_count: int = 0
    deleted_posts: int = 0
    deleted_comments: int = 0
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- 用户操作请求（冻结/解冻原因） ---
class UserActionRequest(BaseModel):
    """用户操作请求"""
    reason: Optional[str] = Field(default=None, description="操作原因", max_length=500)


# --- 分页响应 ---
class PaginatedAdminAuditLogResponse(BaseModel):
    """分页审计日志响应"""
    items: List[AdminAuditLogOut]
    total: int
    page: int
    page_size: int
    has_more: bool


class PaginatedAdminPostResponse(BaseModel):
    """分页管理员帖子响应"""
    items: List[AdminPostOut]
    total: int
    page: int
    page_size: int
    has_more: bool


class PaginatedAdminCommentResponse(BaseModel):
    """分页管理员评论响应"""
    items: List[AdminCommentOut]
    total: int
    page: int
    page_size: int
    has_more: bool


class PaginatedAdminUserResponse(BaseModel):
    """分页管理员用户响应"""
    items: List[AdminUserOut]
    total: int
    page: int
    page_size: int
    has_more: bool


# --- 图表数据 ---

class ActionStatsItem(BaseModel):
    """操作类型统计项"""
    action_type: int = Field(description="操作类型")
    action_name: str = Field(description="操作名称")
    count: int = Field(description="次数")


class ActionStatsResponse(BaseModel):
    """操作统计响应"""
    items: List[ActionStatsItem]
    total: int


class TrendItem(BaseModel):
    """趋势数据项"""
    date: str = Field(description="日期")
    count: int = Field(description="操作数")


class TrendResponse(BaseModel):
    """趋势响应"""
    items: List[TrendItem]
    days: int = Field(description="统计天数")
