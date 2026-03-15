from pydantic import BaseModel
from typing import Optional, List


# --- Vote ---
class VoteCreate(BaseModel):
    post_id: Optional[int] = None  # 为帖子投票
    comment_id: Optional[int] = None  # 为评论投票
    direction: int  # 1 for up, -1 for down


class VoteStatusItem(BaseModel):
    """投票状态项"""
    target_type: str  # 'post' or 'comment'
    target_id: int


class BatchVoteStatusRequest(BaseModel):
    """批量获取投票状态请求"""
    items: List[VoteStatusItem]


class VoteStatusResponse(BaseModel):
    """投票状态响应"""
    target_type: str
    target_id: int
    user_vote: int  # 1, -1, 0
    upvotes: int
    downvotes: int
    score: int