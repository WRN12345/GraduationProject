"""
@Created on : 2025/12/8
@Author: wrn
@Des: 评论路由
"""
from tortoise import models, fields

class Comment(models.Model):
    """评论 (无限层级)"""
    id = fields.IntField(pk=True)
    content = fields.TextField()
    
    post = fields.ForeignKeyField('models.Post', related_name='comments')
    author = fields.ForeignKeyField('models.User', related_name='comments')
    
    # 父评论 ID (自引用)，为空则是根评论
    parent = fields.ForeignKeyField('models.Comment', related_name='replies', null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "comments"

__all__ = ["Comment"]