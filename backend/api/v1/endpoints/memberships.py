"""
@Created on : 2026-01-28
@Author: wrn
@Des: 社区成员管理
"""
from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.transactions import in_transaction
from tortoise.expressions import F
from backend.models.user import User
from backend.models.community import Community
from backend.models.membership import CommunityMembership, MembershipRole
from backend.models.audit_log import AuditLog, ActionType, TargetType
from backend.core.security import get_current_user
from backend.core.permissions import get_community_moderator, get_community_owner, get_current_member
from backend.core.audit import create_audit_log

router = APIRouter(tags=["社区成员管理"])


@router.post("/communities/{community_id}/join", summary="加入社区")
async def join_community(
    community_id: int,
    current_user: User = Depends(get_current_user)
):
    """用户加入社区"""
    # 1. 检查社区是否存在
    community = await Community.get_or_none(id=community_id)
    if not community:
        raise HTTPException(status_code=404, detail="社区不存在")

    # 2. 检查是否已经是成员
    existing = await CommunityMembership.get_or_none(
        user=current_user,
        community_id=community_id
    )
    if existing:
        if existing.role == MembershipRole.BANNED.value:
            raise HTTPException(status_code=403, detail="您已被该社区封禁")
        raise HTTPException(status_code=400, detail="您已经是该社区成员")

    # 3. 创建成员记录
    membership = await CommunityMembership.create(
        user=current_user,
        community_id=community_id,
        role=MembershipRole.MEMBER.value
    )

    # 4. 更新社区成员计数
    await Community.filter(id=community_id).update(
        member_count=F('member_count') + 1
    )

    # 5. 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.COMMUNITY,
        target_id=community_id,
        action_type=ActionType.JOIN_COMMUNITY
    )

    return {"message": "成功加入社区", "role": "成员"}


@router.post("/communities/{community_id}/leave", summary="退出社区")
async def leave_community(
    community_id: int,
    current_user: User = Depends(get_current_user)
):
    """用户退出社区（群主无法退出，需先转移所有权）"""
    membership = await CommunityMembership.get_or_none(
        user=current_user,
        community_id=community_id
    )

    if not membership:
        raise HTTPException(status_code=404, detail="您不是该社区成员")

    if membership.role == MembershipRole.OWNER.value:
        raise HTTPException(
            status_code=400,
            detail="群主无法退出社区，请先转移所有权"
        )

    await membership.delete()

    # 更新成员计数
    await Community.filter(id=community_id).update(
        member_count=F('member_count') - 1
    )

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.COMMUNITY,
        target_id=community_id,
        action_type=ActionType.LEAVE_COMMUNITY
    )

    return {"message": "成功退出社区"}


@router.get("/communities/{community_id}/members", summary="获取社区成员列表")
async def list_community_members(
    community_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """获取社区成员列表"""
    # 验证用户是成员
    await get_current_member(community_id, current_user)

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
            "joined_at": m.joined_at.isoformat(),
            "username": m.user.username,
            "nickname": m.user.nickname,
            "karma": m.user.karma
        })

    return result


@router.post("/communities/{community_id}/members/{user_id}/ban", summary="封禁用户")
async def ban_user(
    community_id: int,
    user_id: int,
    reason: str = None,
    current_user: User = Depends(get_current_user)
):
    """封禁用户（仅版主）"""
    # 验证操作者权限
    actor_membership = await get_community_moderator(community_id, current_user)

    # 获取目标用户成员信息
    target_membership = await CommunityMembership.get_or_none(
        user_id=user_id,
        community_id=community_id
    )

    if not target_membership:
        raise HTTPException(status_code=404, detail="目标用户不是社区成员")

    # 不能封禁群主或更高权限的用户
    if target_membership.role >= actor_membership.role:
        raise HTTPException(status_code=403, detail="无法封禁同级或更高级别的用户")

    # 更新角色为黑名单
    target_membership.role = MembershipRole.BANNED.value
    await target_membership.save()

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.USER,
        target_id=user_id,
        action_type=ActionType.BAN_USER,
        reason=reason,
        metadata={"community_id": community_id}
    )

    return {"message": "用户已被封禁"}


@router.post("/communities/{community_id}/members/{user_id}/unban", summary="解封用户")
async def unban_user(
    community_id: int,
    user_id: int,
    reason: str = None,
    current_user: User = Depends(get_current_user)
):
    """解封用户（仅版主）"""
    await get_community_moderator(community_id, current_user)

    target_membership = await CommunityMembership.get_or_none(
        user_id=user_id,
        community_id=community_id,
        role=MembershipRole.BANNED.value
    )

    if not target_membership:
        raise HTTPException(status_code=404, detail="目标用户未被封禁")

    # 恢复为普通成员
    target_membership.role = MembershipRole.MEMBER.value
    await target_membership.save()

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.USER,
        target_id=user_id,
        action_type=ActionType.UNBAN_USER,
        reason=reason,
        metadata={"community_id": community_id}
    )

    return {"message": "用户已解封"}


@router.post("/communities/{community_id}/members/{user_id}/promote", summary="提升为管理员")
async def promote_to_admin(
    community_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """提升用户为管理员（仅群主）"""
    await get_community_owner(community_id, current_user)

    target_membership = await CommunityMembership.get_or_none(
        user_id=user_id,
        community_id=community_id
    )

    if not target_membership:
        raise HTTPException(status_code=404, detail="目标用户不是社区成员")

    if target_membership.role != MembershipRole.MEMBER.value:
        raise HTTPException(status_code=400, detail="只能提升普通成员为管理员")

    target_membership.role = MembershipRole.ADMIN.value
    await target_membership.save()

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.USER,
        target_id=user_id,
        action_type=ActionType.PROMOTE_ADMIN,
        metadata={"community_id": community_id}
    )

    return {"message": "用户已提升为管理员"}


@router.post("/communities/{community_id}/members/{user_id}/demote", summary="降级为成员")
async def demote_admin(
    community_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """降级管理员为成员（仅群主）"""
    await get_community_owner(community_id, current_user)

    target_membership = await CommunityMembership.get_or_none(
        user_id=user_id,
        community_id=community_id,
        role=MembershipRole.ADMIN.value
    )

    if not target_membership:
        raise HTTPException(status_code=404, detail="目标用户不是管理员")

    target_membership.role = MembershipRole.MEMBER.value
    await target_membership.save()

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.USER,
        target_id=user_id,
        action_type=ActionType.DEMOTE_ADMIN,
        metadata={"community_id": community_id}
    )

    return {"message": "管理员已降级为成员"}


@router.post("/communities/{community_id}/transfer-ownership", summary="转让社区所有权")
async def transfer_ownership(
    community_id: int,
    target_user_id: int,
    current_user: User = Depends(get_current_user)
):
    """转移社区所有权（原子操作）"""
    # 使用事务确保原子性
    async with in_transaction():
        # 验证当前群主
        owner_membership = await get_community_owner(community_id, current_user)

        # 获取目标用户
        target_membership = await CommunityMembership.select_for_update().get_or_none(
            user_id=target_user_id,
            community_id=community_id
        )

        if not target_membership:
            raise HTTPException(status_code=404, detail="目标用户不是社区成员")

        # 目标用户必须是管理员
        if target_membership.role != MembershipRole.ADMIN.value:
            raise HTTPException(status_code=400, detail="只能转移给管理员")

        # 执行转移
        owner_membership.role = MembershipRole.ADMIN.value
        target_membership.role = MembershipRole.OWNER.value

        await owner_membership.save()
        await target_membership.save()

        # 更新社区创建者字段（保持一致性）
        await Community.filter(id=community_id).update(creator_id=target_user_id)

        # 记录审计日志
        await create_audit_log(
            actor=current_user,
            target_type=TargetType.COMMUNITY,
            target_id=community_id,
            action_type=ActionType.TRANSFER_OWNERSHIP,
            metadata={
                "previous_owner": current_user.id,
                "new_owner": target_user_id
            }
        )

    return {"message": "所有权已成功转移"}


@router.get("/feed", summary="获取我的动态流")
async def get_my_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """获取用户加入的所有社区的帖子"""
    # 获取用户加入的社区ID列表
    memberships = await CommunityMembership.filter(
        user=current_user,
        role__gte=MembershipRole.MEMBER.value  # 排除黑名单
    ).values_list('community_id', flat=True)

    if not memberships:
        return []

    # 查询这些社区的帖子
    from backend.models.post import Post
    posts = await Post.filter(
        community_id__in=memberships,
        deleted_at__isnull=True
    ).order_by("-created_at").offset(skip).limit(limit).prefetch_related('author', 'community')

    return posts


__all__ = ["router"]
