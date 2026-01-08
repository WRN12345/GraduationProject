"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.postgres.fields import TSVectorField

class Post(models.Model):
    """帖子"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField(null=True) # Markdown 内容
    
    # 关联
    community = fields.ForeignKeyField('models.Community', related_name='posts')
    author = fields.ForeignKeyField('models.User', related_name='posts')
    
    # 数据统计 (配合 Redis 使用，数据库做持久化备份)
    upvotes = fields.IntField(default=0)
    downvotes = fields.IntField(default=0)
    score = fields.IntField(default=0) # score = up - down
    
    created_at = fields.DatetimeField(auto_now_add=True)

    search_vector = TSVectorField() 

    class Meta:
        table = "posts"

__all__ = ["Post"]