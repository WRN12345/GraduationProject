"""
@Created on : 2026.3.13
@Author: wrn
@Des: 收藏相关的 Schema 定义
"""
from pydantic import BaseModel
from typing import Optional, List


class BookmarkCreate(BaseModel):
    """创建收藏请求"""
    post_id: int
    folder: Optional[str] = "default"
    note: Optional[str] = None


class BookmarkDetail(BaseModel):
    """收藏详情"""
    post_id: int
    title: str
    author: str
    created_at: str
    bookmarked_at: str


class BookmarkListResponse(BaseModel):
    """收藏列表响应"""
    items: List[BookmarkDetail]
    total: int
    skip: int
    limit: int
    has_more: bool


class BookmarkCheckRequest(BaseModel):
    """批量检查收藏状态请求"""
    post_ids: List[int]


class BookmarkCheckResponse(BaseModel):
    """批量检查收藏状态响应"""
    bookmarked: dict  # {post_id: bool}


__all__ = [
    "BookmarkCreate",
    "BookmarkDetail",
    "BookmarkListResponse",
    "BookmarkCheckRequest",
    "BookmarkCheckResponse"
]
