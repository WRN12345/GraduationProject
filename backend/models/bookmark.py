"""
@Created on : 2026.3.13
@Author: wrn
@Des: 收藏/书签模型
"""
from tortoise import models, fields


class Bookmark(models.Model):
    """收藏模型 - 用户收藏帖子"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='bookmarks')
    post = fields.ForeignKeyField('models.Post', related_name='bookmarks')

    # 收藏分类/文件夹（可选）
    folder = fields.CharField(max_length=100, null=True, default="default")

    # 收藏备注（可选）
    note = fields.TextField(null=True, max_length=500)

    created_at = fields.DatetimeField(auto_now_add=False)

    class Meta:
        table = "bookmarks"
        # 联合唯一索引：一个用户对一个帖子只能收藏一次
        unique_together = (("user", "post"),)


__all__ = ["Bookmark"]
