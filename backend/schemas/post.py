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

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    score: int
    author_id: int
    community_id: int
    created_at: datetime

    
    class Config:
        from_attributes = True