"""
@Created on : 2025/12/8
@Author: wrn
@Des: 帖子路由
"""
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.postgres.fields import TSVectorField
import math

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

    # 热度排名
    hot_rank = fields.FloatField(default=0.0, description="热度排名分数")

    # 软删除和编辑跟踪
    deleted_at = fields.DatetimeField(null=True, description="软删除时间戳")
    is_edited = fields.BooleanField(default=False, description="是否被编辑过")

    # 帖子状态管理
    is_locked = fields.BooleanField(default=False, description="禁止新增评论")
    is_highlighted = fields.BooleanField(default=False, description="精华内容")
    is_pinned = fields.BooleanField(default=False, description="置顶帖子")
    deleted_by_id = fields.IntField(null=True, description="谁删除了该帖子")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 全文搜索向量（需要特殊处理）
    # 暂时禁用，因为这可能导致初始化问题
    # search_vector = TSVectorField()

    class Meta:
        table = "posts"

    def calculate_hot_rank(self) -> float:
        """
        计算 Reddit 风格的热度分数
        公式: log10(|score|) + (timestamp / 45000)
        """
        score = self.upvotes - self.downvotes
        if score == 0:
            return 0.0

        # 时间组件（Unix 时间戳秒数）
        epoch_seconds = int(self.created_at.timestamp())

        # Wilson score 区间的简化版本
        # 这会给获得更多投票的帖子更高的排名
        order = math.log10(max(abs(score), 1))

        # 时间衰减：新帖子排名更高
        # 45000 = 12.5 小时
        hot_score = order + (epoch_seconds / 45000)

        return round(hot_score, 7)

    async def update_hot_rank(self):
        """重新计算并保存 hot_rank"""
        self.hot_rank = self.calculate_hot_rank()
        await self.save()

__all__ = ["Post"]