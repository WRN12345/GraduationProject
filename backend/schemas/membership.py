"""
@Created on : 2026-01-28
@Author: wrn
@Des: 成员相关 Pydantic 模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MembershipOut(BaseModel):
    """成员信息输出"""
    id: int
    user_id: int
    community_id: int
    role: int
    joined_at: datetime
    # 可以添加嵌套的用户信息
    username: Optional[str] = None
    nickname: Optional[str] = None

    class Config:
        from_attributes = True


class MembershipListOut(BaseModel):
    """成员列表输出（包含更多用户信息）"""
    id: int
    role: int
    joined_at: datetime
    username: str
    nickname: Optional[str]
    karma: Optional[int]

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    """审计日志输出"""
    id: int
    actor_id: int
    actor_username: str
    target_type: int
    target_id: int
    action_type: int
    reason: Optional[str]
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True


__all__ = ["MembershipOut", "MembershipListOut", "AuditLogOut"]
