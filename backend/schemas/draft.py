"""
@Created on : 2026/3/31
@Author: wrn
@Des: 草稿相关的 Schema 定义
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class DraftCreate(BaseModel):
    """创建草稿请求"""
    title: str = ""
    content: str = ""
    community_id: Optional[int] = None
    attachment_ids: List[int] = []


class DraftUpdate(BaseModel):
    """更新草稿请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    community_id: Optional[int] = None
    attachment_ids: Optional[List[int]] = None


class DraftCommunity(BaseModel):
    """草稿关联社区信息"""
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class DraftOut(BaseModel):
    """草稿信息"""
    id: int
    title: str
    content: Optional[str]
    author_id: int
    community_id: Optional[int]
    community: Optional[DraftCommunity] = None
    attachment_ids: Optional[List[int]] = []
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PaginatedDraftResponse(BaseModel):
    """分页草稿响应"""
    items: List[DraftOut]
    total: int
    skip: int
    limit: int
    has_more: bool


__all__ = [
    "DraftCreate",
    "DraftUpdate",
    "DraftOut",
    "DraftCommunity",
    "PaginatedDraftResponse",
]
