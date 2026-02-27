"""
@Created on : 2026-01-28
@Author: wrn
@Des: 权限依赖函数 - 社区和帖子级别的权限检查
"""
from fastapi import Depends, HTTPException, status
from models.user import User
from models.community import Community
from models.membership import CommunityMembership, MembershipRole
from models.post import Post
from models.comment import Comment
from core.security import get_current_user


async def get_current_member(
    community_id: int,
    current_user: User = Depends(get_current_user)
) -> CommunityMembership:
    """
    获取当前用户在指定社区的成员信息
    如果用户不是成员，返回403
    """
    membership = await CommunityMembership.get_or_none(
        user=current_user,
        community_id=community_id
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该社区的成员"
        )

    if membership.role == MembershipRole.BANNED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您已被该社区封禁"
        )

    return membership


async def get_community_moderator(
    community_id: int,
    current_user: User = Depends(get_current_user)
) -> CommunityMembership:
    """
    验证用户是否为社区版主（管理员或群主）
    """
    membership = await get_current_member(community_id, current_user)

    if not membership.is_moderator():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅版主可操作"
        )

    return membership


async def get_community_owner(
    community_id: int,
    current_user: User = Depends(get_current_user)
) -> CommunityMembership:
    """
    验证用户是否为社区群主
    """
    membership = await get_current_member(community_id, current_user)

    if membership.role != MembershipRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅群主可操作"
        )

    return membership


async def can_post_in_community(
    community_id: int,
    current_user: User = Depends(get_current_user)
) -> CommunityMembership:
    """
    验证用户是否可以在指定社区发帖
    - 必须是成员
    - 不能被禁言/封禁
    """
    membership = await get_current_member(community_id, current_user)
    return membership


async def can_comment_on_post(
    post_id: int,
    current_user: User = Depends(get_current_user)
) -> Post:
    """
    验证用户是否可以评论指定帖子
    - 帖子未锁定
    - 用户在帖子所属社区有权限（如非成员则自动加入）
    """
    post = await Post.get_or_none(id=post_id).prefetch_related('community')

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    if post.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该帖子已被锁定，禁止新增评论"
        )

    # 检查用户是否为社区成员
    membership = await CommunityMembership.get_or_none(
        user=current_user,
        community_id=post.community_id
    )

    # 如果不是成员，自动加入（但排除被封禁的情况）
    if not membership:
        await CommunityMembership.create(
            user=current_user,
            community_id=post.community_id,
            role=MembershipRole.MEMBER.value
        )
    elif membership.role == MembershipRole.BANNED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您已被该社区封禁"
        )

    return post


async def can_moderate_post(
    post_id: int,
    current_user: User = Depends(get_current_user)
) -> tuple[Post, CommunityMembership | None]:
    """
    验证用户是否可以管理指定帖子
    - 版主可以操作帖子
    - 帖子作者可以编辑自己的帖子
    """
    post = await Post.get_or_none(id=post_id).prefetch_related('community')

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    # 如果是作者，可以编辑
    if post.author_id == current_user.id:
        return post, None

    # 如果是版主，可以管理
    membership = await get_community_moderator(post.community_id, current_user)
    return post, membership


async def require_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    验证用户是否为超级管理员
    用于恢复删除内容等敏感操作
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅超级管理员可操作"
        )
    return current_user


__all__ = [
    "get_current_member",
    "get_community_moderator",
    "get_community_owner",
    "can_post_in_community",
    "can_comment_on_post",
    "can_moderate_post",
    "require_superuser",
]
