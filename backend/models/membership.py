"""
@Created on : 2026-01-28
@Author: wrn
@Des: 社区成员关系模型
"""
from tortoise import models, fields
from enum import IntEnum


class MembershipRole(IntEnum):
    """角色枚举"""
    MEMBER = 0      # 普通成员
    ADMIN = 1       # 管理员
    OWNER = 2       # 群主
    BANNED = -1     # 黑名单


class CommunityMembership(models.Model):
    """社区成员关系 - Many-to-Many between User and Community"""
    id = fields.IntField(pk=True)

    # 关系
    user = fields.ForeignKeyField('models.User', related_name='memberships')
    community = fields.ForeignKeyField('models.Community', related_name='memberships')

    # 角色和状态
    role = fields.IntField(default=MembershipRole.MEMBER.value, description="角色: -1=黑名单, 0=成员, 1=管理员, 2=群主")

    # 时间戳
    joined_at = fields.DatetimeField(auto_now_add=True, description="加入时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "community_memberships"
        # 联合唯一索引：一个用户在一个社区只能有一条记录
        unique_together = (("user", "community"),)
        ordering = ["-role", "-joined_at"]

    def __str__(self):
        return f"{self.community.name} - {self.user.username} ({self.get_role_display()})"

    def get_role_display(self):
        """获取角色显示名称"""
        role_map = {
            MembershipRole.OWNER.value: "群主",
            MembershipRole.ADMIN.value: "管理员",
            MembershipRole.MEMBER.value: "成员",
            MembershipRole.BANNED.value: "黑名单",
        }
        return role_map.get(self.role, "未知")

    def is_moderator(self) -> bool:
        """检查是否为版主（管理员或群主）"""
        return self.role >= MembershipRole.ADMIN.value


__all__ = ["CommunityMembership", "MembershipRole"]
