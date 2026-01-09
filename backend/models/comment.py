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

    # 投票统计
    upvotes = fields.IntField(default=0)
    downvotes = fields.IntField(default=0)
    score = fields.IntField(default=0)  # score = up - down

    # 软删除和编辑跟踪
    deleted_at = fields.DatetimeField(null=True, description="软删除时间戳")
    is_edited = fields.BooleanField(default=False, description="是否被编辑过")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "comments"

__all__ = ["Comment"]