"""
@Created on : 2025/12/8
@Author: wrn
@Des: 点赞投票
"""
from tortoise import models, fields

class Vote(models.Model):
    """投票记录 - 支持帖子和评论"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='votes')
    post = fields.ForeignKeyField('models.Post', related_name='post_votes', null=True)
    comment = fields.ForeignKeyField('models.Comment', related_name='comment_votes', null=True)
    # 1: Up, -1: Down
    direction = fields.IntField()

    class Meta:
        table = "votes"
        # 联合唯一索引：确保一个用户对一个帖子或评论只能投一次票
        # 注意：由于 null 值在唯一约束中的处理，我们需要分开定义

__all__ = ["Vote"]