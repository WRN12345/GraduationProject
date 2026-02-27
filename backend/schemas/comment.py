from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None # 如果是回复别人的评论

class CommentUpdate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    content: str
    author_id: int
    author_name: Optional[str] = None  # 作者用户名
    parent_id: Optional[int]
    upvotes: int
    downvotes: int
    score: int
    is_edited: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    replies: List['CommentOut'] = [] # 嵌套
    reply_count: int = 0  # 子评论总数
    has_more_replies: bool = False  # 是否有更多子评论


    class Config:
        from_attributes = True


# 新增：子评论响应 Schema
class CommentRepliesResponse(BaseModel):
    replies: List[CommentOut]
    total: int
    has_more: bool


# 更新前向引用
CommentOut.model_rebuild()