from pydantic import BaseModel
from typing import Optional

# --- Vote ---
class VoteCreate(BaseModel):
    post_id: Optional[int] = None  # 为帖子投票
    comment_id: Optional[int] = None  # 为评论投票
    direction: int  # 1 for up, -1 for down