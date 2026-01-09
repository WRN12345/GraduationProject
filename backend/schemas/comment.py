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
    parent_id: Optional[int]
    upvotes: int
    downvotes: int
    score: int
    is_edited: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    replies: List['CommentOut'] = [] # 嵌套


    class Config:
        from_attributes = True