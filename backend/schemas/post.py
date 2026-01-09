"""
@Created on : 2025/12/8
@Author: wrn
@Des: 请求参数验证模式（手动定义）
"""


from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Post ---
class PostCreate(BaseModel):
    title: str
    content: str
    community_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    score: int
    hot_rank: float
    author_id: int
    community_id: int
    upvotes: int
    downvotes: int
    is_edited: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


    class Config:
        from_attributes = True