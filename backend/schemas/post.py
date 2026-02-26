"""
@Created on : 2025/12/8
@Author: wrn
@Des: 请求参数验证模式（手动定义）
"""


from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

# 避免循环导入
if TYPE_CHECKING:
    from schemas.user import UserOut
    from schemas.community import CommunityOut

# --- Attachment ---
class AttachmentOut(BaseModel):
    """附件信息"""
    id: int
    attachment_type: str
    file_name: str
    file_url: str
    file_size: int
    mime_type: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# --- Post ---
class PostCreate(BaseModel):
    title: str
    content: str
    community_id: int
    attachment_ids: List[int] = []  # 关联的附件 ID 列表


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    attachment_ids: Optional[List[int]] = None  # 更新附件列表

# 定义内嵌的 Author 和 Community schema
class PostAuthor(BaseModel):
    """帖子作者信息（简化版）"""
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class PostCommunity(BaseModel):
    """帖子社区信息（简化版）"""
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class PostOut(BaseModel):
    """帖子信息（包含作者和社区关联对象）"""
    id: int
    title: str
    content: Optional[str]
    score: int
    hot_rank: float
    author_id: int
    community_id: int
    author: Optional[PostAuthor] = None
    community: Optional[PostCommunity] = None
    attachments: List[AttachmentOut] = []  # 附件列表
    upvotes: int
    downvotes: int
    is_edited: bool
    is_locked: bool = False
    is_highlighted: bool = False
    is_pinned: bool = False
    deleted_by_id: Optional[int] = None
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PaginatedPostResponse(BaseModel):
    """分页帖子响应"""
    items: List[PostOut]
    total: int
    skip: int
    limit: int
    has_more: bool  # 是否有更多数据

    model_config = ConfigDict(from_attributes=True)