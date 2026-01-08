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
    created_at = fields.DatetimeField(auto_now_add=True, description="注册时间")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")

    class Meta:
        table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username
    

    class PydanticMeta:
        exclude = ["password"]

__all__ = ["User"]