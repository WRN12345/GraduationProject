"""
@Created on : 2026-01-28
@Author: wrn
@Des: 审计日志辅助函数
"""
from typing import Optional, Dict, Any
from models.audit_log import AuditLog, ActionType, TargetType
from models.user import User


async def create_audit_log(
    actor: User,
    target_type: TargetType,
    target_id: int,
    action_type: ActionType,
    reason: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    创建审计日志记录

    Args:
        actor: 执行操作的用户
        target_type: 目标类型
        target_id: 目标对象ID
        action_type: 操作类型
        reason: 操作原因（可选）
        metadata: 额外的上下文信息（可选）

    Returns:
        AuditLog: 创建的审计日志对象
    """
    return await AuditLog.create(
        actor=actor,
        target_type=target_type.value,
        target_id=target_id,
        action_type=action_type.value,
        reason=reason,
        metadata=metadata or {}
    )


__all__ = ["create_audit_log"]
