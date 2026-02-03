"""
@Created on : 2025/12/8
@Author: wrn
@Des: 搜索相关的 Pydantic Schema
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any


class PostSearchResult(BaseModel):
    """帖子搜索结果"""
    id: int
    title: str
    content: Optional[str]
    author_id: int
    community_id: int
    score: int
    upvotes: int
    downvotes: int
    hot_rank: float
    created_at: Any
    updated_at: Optional[Any]
    rank: Optional[float] = None  # 相关性评分
    highlighted_title: Optional[str] = None  # 高亮标题
    highlighted_content: Optional[str] = None  # 高亮内容


class CommentSearchResult(BaseModel):
    """评论搜索结果"""
    id: int
    content: str
    post_id: int
    author_id: int
    score: int
    upvotes: int
    downvotes: int
    created_at: Any
    highlighted_content: Optional[str] = None


class UserSearchResult(BaseModel):
    """用户搜索结果"""
    id: int
    username: str
    nickname: Optional[str] = None
    karma: int = 0
    is_superuser: bool = False
    created_at: Optional[Any] = None


class UnifiedSearchResponse(BaseModel):
    """统一搜索响应 - 同时返回帖子、评论、用户"""
    posts: List[PostSearchResult]
    comments: List[CommentSearchResult]
    users: List[UserSearchResult]
    total: int  # 总结果数
    query: str  # 搜索关键词


__all__ = [
    "PostSearchResult",
    "CommentSearchResult",
    "UserSearchResult",
    "UnifiedSearchResponse",
]
