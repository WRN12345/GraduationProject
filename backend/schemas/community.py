from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CommunityOut(BaseModel):
    """社区信息"""
    id: int
    name: str
    description: Optional[str] = None
    member_count: int = 0
    post_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunityRecommendation(BaseModel):
    """社区推荐结果"""
    id: int
    name: str
    description: Optional[str]
    member_count: int
    match_score: float = 0  # 匹配分数

    model_config = ConfigDict(from_attributes=True)


