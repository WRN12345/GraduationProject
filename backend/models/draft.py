"""
@Created on : 2026/3/31
@Author: wrn
@Des: 草稿模型
"""
from tortoise import models, fields


class Draft(models.Model):
    """草稿模型 - 用户帖子草稿"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, default="")
    content = fields.TextField(null=True, default="")
    
    # 关联
    author = fields.ForeignKeyField('models.User', related_name='drafts')
    community = fields.ForeignKeyField('models.Community', related_name='drafts', null=True)
    
    # 附件ID列表（JSON格式存储）
    attachment_ids = fields.JSONField(default=list, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "drafts"
        ordering = ["-updated_at"]


__all__ = ["Draft"]
