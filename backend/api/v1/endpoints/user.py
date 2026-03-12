"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户相关路由
"""

from gc import get_count
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from models.user import User
from models.post import Post
from models.comment import Comment
from schemas import UserUpdate, User_Pydantic
from schemas.user import UserProfile, UserActivity, UserInfo, UsernameUpdate, PasswordUpdate, UserProfileUpdate
from core.security import get_current_user, get_password_hash, verify_password
from core.minio_service import minio_service

# 鉴权
user = APIRouter(tags=["用户相关"], dependencies=[Depends(get_current_user)])


# --- 获取当前用户 ---
@user.get("/users", summary="获取当前用户信息", response_model=UserInfo)
async def user_info(user_obj: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    不需要额外参数，直接通过 Token 解析身份
    返回用户的实际数据，包括昵称、邮箱、简介、头像等
    """
    return UserInfo(
        id=user_obj.id,
        username=user_obj.username,
        nickname=user_obj.nickname,
        email=user_obj.email,
        bio=user_obj.bio,
        avatar=user_obj.avatar,
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
    可以更新昵称、邮箱、个人简介、头像
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
        avatar=user_obj.avatar,
        karma=user_obj.karma,
        is_active=user_obj.is_active,
        is_superuser=user_obj.is_superuser,
        created_at=user_obj.created_at,
        last_login=user_obj.last_login
    )


# --- 修改用户名 ---
@user.put("/users/username", summary="修改用户名", response_model=UserInfo)
async def update_username(
    username_form: UsernameUpdate,
    user_obj: User = Depends(get_current_user)
):
    """
    修改用户名
    - 检查新用户名是否已被占用
    - 不允许修改为当前用户名
    """
    # 检查是否与当前用户名相同
    if username_form.username == user_obj.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新用户名不能与当前用户名相同"
        )

    # 检查用户名是否已存在
    existing_user = await User.get_or_none(username=username_form.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被占用"
        )

    # 更新用户名
    await User.filter(id=user_obj.id).update(username=username_form.username)
    await user_obj.refresh_from_db()

    return UserInfo(
        id=user_obj.id,
        username=user_obj.username,
        nickname=user_obj.nickname,
        email=user_obj.email,
        bio=user_obj.bio,
        avatar=user_obj.avatar,
        karma=user_obj.karma,
        is_active=user_obj.is_active,
        is_superuser=user_obj.is_superuser,
        created_at=user_obj.created_at,
        last_login=user_obj.last_login
    )


# --- 修改密码 ---
@user.put("/users/password", summary="修改密码")
async def update_password(
    password_form: PasswordUpdate,
    user_obj: User = Depends(get_current_user)
):
    """
    修改密码
    - 需要提供旧密码进行验证
    """
    # 验证旧密码
    if not verify_password(password_form.old_password, user_obj.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 检查新密码是否与旧密码相同
    if password_form.old_password == password_form.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )

    # 更新密码
    hashed_password = get_password_hash(password_form.new_password)
    await User.filter(id=user_obj.id).update(password=hashed_password)

    return {"message": "密码修改成功"}


# --- 更新用户资料（扩展版） ---
@user.put("/users/profile", summary="更新用户资料", response_model=UserInfo)
async def update_user_profile(
    user_form: UserProfileUpdate,
    user_obj: User = Depends(get_current_user)
):
    """
    更新用户资料(昵称、邮箱、个人简介、头像)
    """
    update_data = user_form.model_dump(exclude_unset=True)

    if update_data:
        await User.filter(id=user_obj.id).update(**update_data)
        await user_obj.refresh_from_db()

    return UserInfo(
        id=user_obj.id,
        username=user_obj.username,
        nickname=user_obj.nickname,
        email=user_obj.email,
        bio=user_obj.bio,
        avatar=user_obj.avatar,
        karma=user_obj.karma,
        is_active=user_obj.is_active,
        is_superuser=user_obj.is_superuser,
        created_at=user_obj.created_at,
        last_login=user_obj.last_login
    )


# --- 上传头像 ---
@user.post("/users/avatar", summary="上传用户头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传用户头像
    - 验证文件类型为图片
    - 最大 5MB
    - 返回头像URL并自动更新用户头像字段
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 文件大小限制
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="头像大小不能超过 5MB")

    # 上传到 MinIO
    url = await minio_service.upload_file(
        file_data=content,
        filename=f"avatar_{current_user.id}_{file.filename}",
        content_type=file.content_type
    )

    # 更新用户头像
    await User.filter(id=current_user.id).update(avatar=url)
    await current_user.refresh_from_db()

    return {
        "avatar_url": url,
        "message": "头像上传成功"
    }


# --- 公开用户资料（无需登录） ---
from fastapi import APIRouter

user_public = APIRouter(tags=["用户资料（公开）"])

@user_public.get("/users/{username}", response_model=UserProfile,summary="获取公开用户资料")
async def get_user_profile(username: str):
    """获取公开用户资料"""
    user = await User.get_or_none(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 计算统计数据   
    post_count = await Post.filter(author=user, deleted_at__isnull=True).count()
    comment_count = await Comment.filter(author=user, deleted_at__isnull=True).count()

    # 如果 karma 为 0，触发计算
    if user.karma == 0:
        await user.calculate_karma()
        await user.refresh_from_db()

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "bio": user.bio,
        "avatar": user.avatar,
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
    user = await User.get_or_none(username=username)    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    posts = await Post.filter(
        author=user,
        deleted_at__isnull=True
    ).order_by("-created_at").offset(skip).limit(limit)

    return posts

@user_public.get("/users/{username}/comments", summary="获取用户发表的评论")
async def get_user_comments(
    username: str,
    skip: int = 0,
    limit: int = 50,
):
    """获取用户发表的评论（使用主库）"""
    user = await User.get_or_none(username=username)    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    comments = await Comment.filter(
        author=user,
        deleted_at__isnull=True
    ).order_by("-created_at").offset(skip).limit(limit)

    return comments

@user_public.get("/users/{username}/activity", response_model=UserActivity, summary="获取用户的活动汇总")
async def get_user_activity(username: str):
    """获取用户的活动汇总（帖子和评论）"""
    user = await User.get_or_none(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取最近的帖子
    posts = await Post.filter(
        author=user,
        deleted_at__isnull=True
    ).order_by("-created_at").limit(10).values()

    # 获取最近的评论
    comments = await Comment.filter(
        author=user,
        deleted_at__isnull=True
    ).order_by("-created_at").limit(10).values()

    # 获取总数
    total_posts = await Post.filter(author=user).count()
    total_comments = await Comment.filter(author=user).count()

    return {
        "posts": list(posts),
        "comments": list(comments),
        "total_posts": total_posts,
        "total_comments": total_comments,
    }


__all__ = [
    "user",
    "user_public"
]