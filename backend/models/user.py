"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户数据模型
"""

from tortoise import models, fields

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, null=False, unique=True, index=True, description="账户")
    password = fields.CharField(max_length=255, null=False, description="密码(Hash)")
    nickname = fields.CharField(max_length=50, null=True, description="昵称", default="新用户")
    email = fields.CharField(max_length=100, null=True, unique=True, description="邮箱")
    
    # --- 审计与状态 ---
    is_active = fields.BooleanField(default=True, description="是否激活/冻结")
    is_superuser = fields.BooleanField(default=False, description="是否管理员")
    karma = fields.IntField(default=0, description="声望值（来自帖子和评论的点赞）")
    bio = fields.TextField(null=True, max_length=5000, description="个人简介")
    created_at = fields.DatetimeField(auto_now_add=True, description="注册时间")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")

    class Meta:
        table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    async def calculate_karma(self) -> int:
        """
        计算用户的声望值
        声望 = 帖子获得的点赞数 + 评论获得的点赞数
        """
        from tortoise.functions import Sum
        from backend.models.post import Post
        from backend.models.comment import Comment

        # 计算帖子的总点赞数
        post_result = await Post.filter(author=self).annotate(
            total_upvotes=Sum('upvotes')
        ).values_list('total_upvotes', flat=True)

        post_karma = post_result[0] if post_result and post_result[0] else 0

        # 计算评论的总点赞数
        comment_result = await Comment.filter(author=self).annotate(
            total_upvotes=Sum('upvotes')
        ).values_list('total_upvotes', flat=True)

        comment_karma = comment_result[0] if comment_result and comment_result[0] else 0

        # 更新 karma 字段
        total_karma = post_karma + comment_karma
        self.karma = total_karma
        await self.save()

        return total_karma
    

    class PydanticMeta:
        exclude = ["password"]

__all__ = ["User"]