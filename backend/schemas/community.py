from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CommunityOut(CommunityCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommunityRecommendation(BaseModel):
    """社区推荐结果"""
    id: int
    name: str
    description: Optional[str]
    member_count: int
    match_score: float = 0  # 匹配分数

    class Config:
        from_attributes = True


