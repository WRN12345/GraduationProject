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
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "communities"

__all__ = ["Community"]