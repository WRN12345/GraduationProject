"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户相关路由
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.models.user import User
from backend.models.post import Post
from backend.models.comment import Comment
from backend.schemas import UserUpdate, User_Pydantic
from backend.schemas.user import UserProfile, UserActivity, UserInfo
from backend.core.security import get_current_user, get_password_hash

# 鉴权
user = APIRouter(tags=["用户相关"], dependencies=[Depends(get_current_user)])


# --- 获取当前用户 ---
@user.get("/users", summary="获取当前用户信息", response_model=UserInfo)
async def user_info(user_obj: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    不需要额外参数，直接通过 Token 解析身份
    返回用户的实际数据，包括昵称、邮箱、简介等
    """
    return UserInfo(
        id=user_obj.id,
        username=user_obj.username,
        nickname=user_obj.nickname,
        email=user_obj.email,
        bio=user_obj.bio,
        karma=user_obj.karma,
        is_active=user_obj.is_active,
        is_superuser=user_obj.is_superuser,
        created_at=user_obj.created_at,
        last_login=user_obj.last_login
    )


# --- 更新当前用户 ---
@user.put("/users", summary="更新当前用户信息", response_model=UserInfo)
async def user_update(
    user_form: UserUpdate,
    user_obj: User = Depends(get_current_user)
):
    """
    更新个人信息
    可以更新昵称、邮箱、个人简介
    不允许修改用户名和密码（密码需要单独的接口）

    注意：此接口仅更新提供的字段，未提供的字段保持不变
    """
    update_data = user_form.model_dump(exclude_unset=True)

    # 不允许修改用户名
    if "username" in update_data:
        del update_data["username"]

    if update_data:
        await User.filter(id=user_obj.id).update(**update_data)
        await user_obj.refresh_from_db()

    # 返回更新后的完整用户信息
    return UserInfo(
        id=user_obj.id,
        username=user_obj.username,
        nickname=user_obj.nickname,
        email=user_obj.email,
        bio=user_obj.bio,
        karma=user_obj.karma,
        is_active=user_obj.is_active,
        is_superuser=user_obj.is_superuser,
        created_at=user_obj.created_at,
        last_login=user_obj.last_login
    )


# --- 公开用户资料（无需登录） ---
from fastapi import APIRouter

user_public = APIRouter(tags=["用户资料（公开）"])

@user_public.get("/users/{username}", response_model=UserProfile)
async def get_user_profile(username: str):
    """获取公开用户资料（使用主库）"""
    user = await User.get_or_none(username=username).using_db('master')

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 计算统计数据（使用主库）
    post_count = await Post.filter(author=user, deleted_at__isnull=True).using_db('master').count()
    comment_count = await Comment.filter(author=user, deleted_at__isnull=True).using_db('master').count()

    # 如果 karma 为 0，触发计算
    if user.karma == 0:
        await user.calculate_karma()
        await user.refresh_from_db()

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "bio": user.bio,
        "karma": user.karma,
        "created_at": user.created_at,
        "is_active": user.is_active,
        "post_count": post_count,
        "comment_count": comment_count,
    }

@user_public.get("/users/{username}/posts", summary="获取用户发布的帖子")
async def get_user_posts(
    username: str,
    skip: int = 0,
    limit: int = 20,
):
    """获取用户发布的帖子（使用主库）"""
    user = await User.get_or_none(username=username).using_db('master')
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    posts = await Post.filter(
        author=user,
        deleted_at__isnull=True
    ).using_db('master').order_by("-created_at").offset(skip).limit(limit)

    return posts

@user_public.get("/users/{username}/comments", summary="获取用户发表的评论")
async def get_user_comments(
    username: str,
    skip: int = 0,
    limit: int = 50,
):
    """获取用户发表的评论（使用主库）"""
    user = await User.get_or_none(username=username).using_db('master')
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    comments = await Comment.filter(
        author=user,
        deleted_at__isnull=True
    ).using_db('master').order_by("-created_at").offset(skip).limit(limit)

    return comments

@user_public.get("/users/{username}/activity", response_model=UserActivity, summary="获取用户的活动汇总")
async def get_user_activity(username: str):
    """获取用户的活动汇总（帖子和评论，使用主库）"""
    user = await User.get_or_none(username=username).using_db('master')
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取最近的帖子（使用主库）
    posts = await Post.filter(
        author=user,
        deleted_at__isnull=True
    ).using_db('master').order_by("-created_at").limit(10)

    # 获取最近的评论（使用主库）
    comments = await Comment.filter(
        author=user,
        deleted_at__isnull=True
    ).using_db('master').order_by("-created_at").limit(10)

    # 获取总数（使用主库）
    total_posts = await Post.filter(author=user).using_db('master').count()
    total_comments = await Comment.filter(author=user).using_db('master').count()

    return {
        "posts": posts,
        "comments": comments,
        "total_posts": total_posts,
        "total_comments": total_comments,
    }


__all__ = [
    "user",
    "user_public"
]