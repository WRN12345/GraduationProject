"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户相关路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from models.user import User
from schemas import UserUpdate
from schemas.user import UserProfile, UserActivity, UserInfo, UsernameUpdate, PasswordUpdate, UserProfileUpdate
from core.security import get_current_user
from services.user_service import user_service

# 鉴权
user = APIRouter(tags=["用户相关"], dependencies=[Depends(get_current_user)])


# --- 获取当前用户 ---
@user.get("/users", summary="获取当前用户信息", response_model=UserInfo)
async def user_info(user_obj: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    return await user_service.get_user_info(user_obj)


# --- 更新当前用户 ---
@user.put("/users", summary="更新当前用户信息", response_model=UserInfo)
async def user_update(
    user_form: UserUpdate,
    user_obj: User = Depends(get_current_user)
):
    """更新个人信息"""
    return await user_service.update_user_info(user_obj, **user_form.model_dump(exclude_unset=True))


# --- 修改用户名 ---
@user.put("/users/username", summary="修改用户名", response_model=UserInfo)
async def update_username(
    username_form: UsernameUpdate,
    user_obj: User = Depends(get_current_user)
):
    """修改用户名"""
    result = await user_service.update_username(user_obj, username_form.username)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


# --- 修改密码 ---
@user.put("/users/password", summary="修改密码")
async def update_password(
    password_form: PasswordUpdate,
    user_obj: User = Depends(get_current_user)
):
    """修改密码"""
    result = await user_service.update_password(
        user_obj,
        password_form.old_password,
        password_form.new_password
    )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return result


# --- 更新用户资料（扩展版） ---
@user.put("/users/profile", summary="更新用户资料", response_model=UserInfo)
async def update_user_profile(
    user_form: UserProfileUpdate,
    user_obj: User = Depends(get_current_user)
):
    """更新用户资料(昵称、邮箱、个人简介、头像)"""
    return await user_service.update_user_profile(user_obj, **user_form.model_dump(exclude_unset=True))


# --- 上传头像 ---
@user.post("/users/avatar", summary="上传用户头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传用户头像"""
    content = await file.read()
    result = await user_service.upload_avatar(
        current_user,
        file_data=content,
        filename=file.filename,
        content_type=file.content_type
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# --- 公开用户资料（无需登录） ---
from fastapi import APIRouter

user_public = APIRouter(tags=["用户资料（公开）"])

@user_public.get("/users/{username}", response_model=UserProfile, summary="获取公开用户资料")
async def get_user_profile(username: str):
    """获取公开用户资料"""
    result = await user_service.get_user_profile(username)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@user_public.get("/users/{username}/posts", summary="获取用户发布的帖子")
async def get_user_posts(
    username: str,
    skip: int = 0,
    limit: int = 20,
):
    """获取用户发布的帖子"""
    result = await user_service.get_user_posts(username, skip, limit)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@user_public.get("/users/{username}/comments", summary="获取用户发表的评论")
async def get_user_comments(
    username: str,
    skip: int = 0,
    limit: int = 50,
):
    """获取用户发表的评论"""
    result = await user_service.get_user_comments(username, skip, limit)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@user_public.get("/users/{username}/activity", response_model=UserActivity, summary="获取用户的活动汇总")
async def get_user_activity(username: str):
    """获取用户的活动汇总（帖子和评论）"""
    result = await user_service.get_user_activity(username)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


__all__ = [
    "user",
    "user_public"
]
