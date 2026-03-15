"""
@Created on : 2026-01-8
@Author: wrn
@Des: 社区成员管理
"""
from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from models.membership import CommunityMembership, MembershipRole
from models.post import Post
from core.security import get_current_user
from core.permissions import get_community_moderator, get_community_owner, get_current_member
from services.membership_service import membership_service

router = APIRouter(prefix="/memberships", tags=["社区成员管理"])


@router.post("/communities/{community_id}/join", summary="加入社区")
async def join_community(
    community_id: int,
    current_user: User = Depends(get_current_user)
):
    """用户加入社区"""
    result = await membership_service.join_community(current_user, community_id)

    if "error" in result:
        error_msg = result["error"]
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "封禁" in error_msg:
            raise HTTPException(status_code=403, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return result


@router.post("/communities/{community_id}/leave", summary="退出社区")
async def leave_community(
    community_id: int,
    current_user: User = Depends(get_current_user)
):
    """用户退出社区（群主无法退出，需先转移所有权）"""
    result = await membership_service.leave_community(current_user, community_id)

    if "error" in result:
        error_msg = result["error"]
        if "不是" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return result


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

    return await membership_service.get_community_members(community_id, skip, limit)


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

    result = await membership_service.ban_user(
        community_id=community_id,
        actor=current_user,
        target_user_id=user_id,
        actor_role=actor_membership.role,
        reason=reason
    )

    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])

    return result


@router.post("/communities/{community_id}/members/{user_id}/unban", summary="解封用户")
async def unban_user(
    community_id: int,
    user_id: int,
    reason: str = None,
    current_user: User = Depends(get_current_user)
):
    """解封用户（仅版主）"""
    await get_community_moderator(community_id, current_user)

    result = await membership_service.unban_user(
        community_id=community_id,
        actor=current_user,
        target_user_id=user_id,
        reason=reason
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.post("/communities/{community_id}/members/{user_id}/promote", summary="提升为管理员")
async def promote_to_admin(
    community_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """提升用户为管理员（仅群主）"""
    from models.audit_log import ActionType

    await get_community_owner(community_id, current_user)

    result = await membership_service.update_role(
        community_id=community_id,
        actor=current_user,
        target_user_id=user_id,
        new_role=MembershipRole.ADMIN.value,
        actor_role=MembershipRole.OWNER.value,
        action_type=ActionType.PROMOTE_ADMIN
    )

    if "error" in result:
        error_msg = result["error"]
        if "不是" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=403, detail=error_msg)

    return result


@router.post("/communities/{community_id}/members/{user_id}/demote", summary="降级为成员")
async def demote_admin(
    community_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """降级管理员为成员（仅群主）"""
    from models.audit_log import ActionType

    await get_community_owner(community_id, current_user)

    result = await membership_service.update_role(
        community_id=community_id,
        actor=current_user,
        target_user_id=user_id,
        new_role=MembershipRole.MEMBER.value,
        actor_role=MembershipRole.OWNER.value,
        action_type=ActionType.DEMOTE_ADMIN
    )

    if "error" in result:
        error_msg = result["error"]
        if "不是" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=403, detail=error_msg)

    return result


@router.post("/communities/{community_id}/transfer-ownership", summary="转让社区所有权")
async def transfer_ownership(
    community_id: int,
    target_user_id: int,
    current_user: User = Depends(get_current_user)
):
    """转移社区所有权"""
    await get_community_owner(community_id, current_user)

    result = await membership_service.transfer_ownership(
        community_id=community_id,
        owner=current_user,
        target_user_id=target_user_id
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


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
    posts = await Post.filter(
        community_id__in=memberships,
        deleted_at__isnull=True
    ).order_by("-created_at").offset(skip).limit(limit).prefetch_related('author', 'community')

    return posts


@router.get("/my-communities", summary="获取用户加入的社区列表")
async def get_my_communities(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """获取当前用户加入的所有社区"""
    # 获取用户的所有成员关系（排除黑名单）
    memberships = await CommunityMembership.filter(
        user=current_user,
        role__gte=MembershipRole.MEMBER.value  # 排除 BANNED (-1)
    ).select_related('community').offset(skip).limit(limit)

    # 构建响应数据
    result = []
    for m in memberships:
        # 获取社区帖子数量
        post_count = await Post.filter(
            community_id=m.community.id,
            deleted_at__isnull=True
        ).count()

        result.append({
            "id": m.community.id,
            "name": m.community.name,
            "description": m.community.description,
            "member_count": m.community.member_count,
            "post_count": post_count,
            "role": m.role,
            "role_display": m.get_role_display(),
            "joined_at": m.joined_at.isoformat()
        })

    return result


__all__ = ["router"]
