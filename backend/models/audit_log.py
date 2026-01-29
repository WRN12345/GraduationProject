"""
@Created on : 2026-01-28
@Author: wrn
@Des: 审计日志模型 - 记录所有管理操作
"""
from tortoise import models, fields
from enum import IntEnum


class ActionType(IntEnum):
    """操作类型枚举"""
    # 社区相关
    JOIN_COMMUNITY = 1
    LEAVE_COMMUNITY = 2
    BAN_USER = 3
    UNBAN_USER = 4
    TRANSFER_OWNERSHIP = 5
    PROMOTE_ADMIN = 6
    DEMOTE_ADMIN = 7

    # 帖子相关
    LOCK_POST = 10
    UNLOCK_POST = 11
    HIGHLIGHT_POST = 12
    UNHIGHLIGHT_POST = 13
    PIN_POST = 14
    UNPIN_POST = 15
    DELETE_POST = 16
    RESTORE_POST = 17

    # 评论相关
    DELETE_COMMENT = 20
    RESTORE_COMMENT = 21


class TargetType(IntEnum):
    """目标类型枚举"""
    COMMUNITY = 1
    USER = 2
    POST = 3
    COMMENT = 4


class AuditLog(models.Model):
    """审计日志 - 记录所有管理操作"""
    id = fields.BigIntField(pk=True)

    # 操作者
    actor = fields.ForeignKeyField('models.User', related_name='audit_logs')

    # 目标对象 (使用通用外键模式)
    target_type = fields.IntField(description="目标类型")
    target_id = fields.IntField(description="目标ID")

    # 操作详情
    action_type = fields.IntField(description="操作类型")
    reason = fields.TextField(null=True, max_length=1000, description="操作原因")

    # 额外信息 (JSON格式存储)
    metadata = fields.JSONField(default=dict, description="额外上下文信息")

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True, description="操作时间")

    class Meta:
        table = "audit_logs"
        ordering = ["-created_at"]
        # 索引优化：按操作者、目标类型+ID、操作类型查询
        indexes = [
            ("actor", "created_at"),
            ("target_type", "target_id", "created_at"),
            ("action_type", "created_at"),
        ]

    def __str__(self):
        return f"AuditLog {self.id}: {self.actor.username} -> {self.action_type}"


__all__ = ["AuditLog", "ActionType", "TargetType"]
