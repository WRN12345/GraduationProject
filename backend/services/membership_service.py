"""
@Created on : 2026/3/15
@Author: wrn
@Des: 成员服务 - 成员管理 + 权限控制
"""
from typing import Optional
from tortoise.expressions import F
from models.user import User
from models.community import Community
from models.membership import CommunityMembership, MembershipRole
from models.audit_log import ActionType, TargetType
from core.audit import create_audit_log
import logging

logger = logging.getLogger(__name__)


class MembershipService:
    """成员服务 - 成员管理 + 权限控制"""

    async def join_community(
        self,
        user: User,
        community_id: int
    ) -> dict:
        """
        加入社区

        Args:
            user: 当前用户
            community_id: 社区 ID

        Returns:
            dict: 加入结果

        Raises:
            Returns {"error": "..."} on failure
        """
        # 1. 检查社区是否存在
        community = await Community.get_or_none(id=community_id)
        if not community:
            return {"error": "社区不存在"}

        # 2. 检查是否已经是成员
        existing = await CommunityMembership.get_or_none(
            user=user,
            community_id=community_id
        )
        if existing:
            if existing.role == MembershipRole.BANNED.value:
                return {"error": "您已被该社区封禁"}
            return {"error": "您已经是该社区成员"}

        # 3. 创建成员记录
        membership = await CommunityMembership.create(
            user=user,
            community_id=community_id,
            role=MembershipRole.MEMBER.value
        )

        # 4. 更新社区成员计数
        await Community.filter(id=community_id).update(
            member_count=F('member_count') + 1
        )

        # 5. 记录审计日志
        await create_audit_log(
            actor=user,
            target_type=TargetType.COMMUNITY,
            target_id=community_id,
            action_type=ActionType.JOIN_COMMUNITY
        )

        return {"message": "成功加入社区", "role": "成员"}

    async def leave_community(
        self,
        user: User,
        community_id: int
    ) -> dict:
        """
        退出社区

        Args:
            user: 当前用户
            community_id: 社区 ID

        Returns:
            dict: 退出结果

        Raises:
            Returns {"error": "..."} on failure
        """
        membership = await CommunityMembership.get_or_none(
            user=user,
            community_id=community_id
        )

        if not membership:
            return {"error": "您不是该社区成员"}

        if membership.role == MembershipRole.OWNER.value:
            return {"error": "群主无法退出社区，请先转移所有权"}

        await membership.delete()

        # 更新成员计数
        await Community.filter(id=community_id).update(
            member_count=F('member_count') - 1
        )

        # 记录审计日志
        await create_audit_log(
            actor=user,
            target_type=TargetType.COMMUNITY,
            target_id=community_id,
            action_type=ActionType.LEAVE_COMMUNITY
        )

        return {"message": "成功退出社区"}

    async def get_community_members(
        self,
        community_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> list:
        """
        获取社区成员列表

        Args:
            community_id: 社区 ID
            skip: 跳过条数
            limit: 返回条数

        Returns:
            list: 成员列表
        """
        memberships = await CommunityMembership.filter(
            community_id=community_id
        ).offset(skip).limit(limit).prefetch_related('user')

        result = []
        for m in memberships:
            result.append({
                "id": m.id,
                "user_id": m.user_id,
                "role": m.role,
                "role_display": m.get_role_display(),
                "joined_at": m.joined_at,  # 保持 datetime 对象
                "username": m.user.username,
                "nickname": m.user.nickname,
                "karma": m.user.karma
            })

        return result

    async def ban_user(
        self,
        community_id: int,
        actor: User,
        target_user_id: int,
        actor_role: int,
        reason: Optional[str] = None
    ) -> dict:
        """
        封禁用户

        Args:
            community_id: 社区 ID
            actor: 操作者
            target_user_id: 目标用户 ID
            actor_role: 操作者角色
            reason: 原因

        Returns:
            dict: 封禁结果

        Raises:
            Returns {"error": "..."} on failure
        """
        # 获取目标用户成员信息
        target_membership = await CommunityMembership.get_or_none(
            user_id=target_user_id,
            community_id=community_id
        )

        if not target_membership:
            return {"error": "目标用户不是社区成员"}

        # 不能封禁同级或更高级别的用户
        if target_membership.role >= actor_role:
            return {"error": "无法封禁同级或更高级别的用户"}

        # 更新角色为黑名单
        target_membership.role = MembershipRole.BANNED.value
        await target_membership.save()

        # 记录审计日志
        await create_audit_log(
            actor=actor,
            target_type=TargetType.USER,
            target_id=target_user_id,
            action_type=ActionType.BAN_USER,
            reason=reason,
            metadata={"community_id": community_id}
        )

        return {"message": "用户已被封禁"}

    async def unban_user(
        self,
        community_id: int,
        actor: User,
        target_user_id: int,
        reason: Optional[str] = None
    ) -> dict:
        """
        解封用户

        Args:
            community_id: 社区 ID
            actor: 操作者
            target_user_id: 目标用户 ID
            reason: 原因

        Returns:
            dict: 解封结果

        Raises:
            Returns {"error": "..."} on failure
        """
        target_membership = await CommunityMembership.get_or_none(
            user_id=target_user_id,
            community_id=community_id,
            role=MembershipRole.BANNED.value
        )

        if not target_membership:
            return {"error": "目标用户未被封禁"}

        # 恢复为普通成员
        target_membership.role = MembershipRole.MEMBER.value
        await target_membership.save()

        # 记录审计日志
        await create_audit_log(
            actor=actor,
            target_type=TargetType.USER,
            target_id=target_user_id,
            action_type=ActionType.UNBAN_USER,
            reason=reason,
            metadata={"community_id": community_id}
        )

        return {"message": "用户已解封"}

    async def update_role(
        self,
        community_id: int,
        actor: User,
        target_user_id: int,
        new_role: str,
        actor_role: int,
        action_type: ActionType,
        reason: Optional[str] = None
    ) -> dict:
        """
        更新成员角色

        Args:
            community_id: 社区 ID
            actor: 操作者
            target_user_id: 目标用户 ID
            new_role: 新角色
            actor_role: 操作者角色
            action_type: 审计动作类型
            reason: 原因

        Returns:
            dict: 更新结果

        Raises:
            Returns {"error": "..."} on failure
        """
        target_membership = await CommunityMembership.get_or_none(
            user_id=target_user_id,
            community_id=community_id
        )

        if not target_membership:
            return {"error": "目标用户不是社区成员"}

        # 不能修改同级或更高级别的用户
        if target_membership.role >= actor_role:
            return {"error": "无法修改同级或更高级别的用户"}

        # 更新角色
        target_membership.role = new_role
        await target_membership.save()

        # 记录审计日志
        await create_audit_log(
            actor=actor,
            target_type=TargetType.USER,
            target_id=target_user_id,
            action_type=action_type,
            reason=reason,
            metadata={"community_id": community_id, "new_role": new_role}
        )

        return {"message": "角色更新成功"}

    async def transfer_ownership(
        self,
        community_id: int,
        owner: User,
        target_user_id: int
    ) -> dict:
        """
        转让社区所有权

        Args:
            community_id: 社区 ID
            owner: 当前群主
            target_user_id: 目标用户 ID

        Returns:
            dict: 转让结果

        Raises:
            Returns {"error": "..."} on failure
        """
        # 获取当前群主成员信息
        owner_membership = await CommunityMembership.get_or_none(
            user=owner,
            community_id=community_id,
            role=MembershipRole.OWNER.value
        )

        if not owner_membership:
            return {"error": "您不是该社区的群主"}

        # 获取目标用户成员信息
        target_membership = await CommunityMembership.get_or_none(
            user_id=target_user_id,
            community_id=community_id
        )

        if not target_membership:
            return {"error": "目标用户不是社区成员"}

        # 转让所有权
        owner_membership.role = MembershipRole.MODERATOR.value
        await owner_membership.save()

        target_membership.role = MembershipRole.OWNER.value
        await target_membership.save()

        # 记录审计日志
        await create_audit_log(
            actor=owner,
            target_type=TargetType.COMMUNITY,
            target_id=community_id,
            action_type=ActionType.TRANSFER_OWNERSHIP,
            metadata={"new_owner_id": target_user_id}
        )

        return {"message": "所有权转让成功"}

    async def get_user_membership(
        self,
        user_id: int,
        community_id: int
    ) -> Optional[CommunityMembership]:
        """获取用户成员信息"""
        return await CommunityMembership.get_or_none(
            user_id=user_id,
            community_id=community_id
        )


# 导出服务实例
membership_service = MembershipService()

__all__ = ["MembershipService", "membership_service"]
