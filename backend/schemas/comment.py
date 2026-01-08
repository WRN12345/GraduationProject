from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None # 如果是回复别人的评论

class CommentOut(BaseModel):
    id: int
    content: str
    author_id: int
    parent_id: Optional[int]
    created_at: datetime
    replies: List['CommentOut'] = [] # 嵌套

    
    class Config:
        from_attributes = True