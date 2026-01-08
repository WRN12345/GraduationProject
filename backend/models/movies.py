"""
@Created on : 2025/12/8
@Author: wrn
@Des: 电影数据模型
"""

from tortoise import models, fields

class Movie(models.Model):

    id = fields.IntField(pk=True)
    
    name = fields.CharField(max_length=50, null=False, description="电影名称", index=True)
    
    year = fields.IntField(null=False, description="上映年份")
    
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    updated_at = fields.DatetimeField(auto_now=True, description="最后更新时间")

    class Meta:

        table = "movies"
        ordering = ["-year"]

    def __str__(self):
        return f"{self.name} ({self.year})"

__all__ = ["Movie"]