"""
@Created on : 2025/12/8
@Author: wrn
@Des: 社区板块路由
"""
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Community(models.Model):
    """板块 / Subreddit"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, index=True)
    description = fields.TextField(null=True)
    creator = fields.ForeignKeyField('models.User', related_name='created_communities')

    # 统计字段（冗余，提升查询性能）
    member_count = fields.IntField(default=0, description="成员数量")
    post_count = fields.IntField(default=0, description="帖子数量")
    last_active_at = fields.DatetimeField(null=True, description="最后活跃时间")

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "communities"

__all__ = ["Community"]