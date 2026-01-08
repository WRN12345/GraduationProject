"""
@Created on : 2025/12/8
@Author: wrn
@Des: 点赞投票
"""
from tortoise import models, fields

class Vote(models.Model):
    """投票记录"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='votes')
    post = fields.ForeignKeyField('models.Post', related_name='post_votes', null=True)
    # 1: Up, -1: Down
    direction = fields.IntField() 
    
    class Meta:
        table = "votes"
        # 联合唯一索引：确保一个用户对一个帖子只能投一次票
        unique_together = (("user", "post"),)

__all__ = ["Vote"]