"""
@Created on : 2025/12/8
@Author: wrn
@Des: 登录注册路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from schemas import UserCreate
from core.services import auth_service

login = APIRouter(tags=["认证相关"])


# --- Token 响应 ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    is_superuser: bool  # 是否为管理员
    user_id: int  # 用户 ID


class TokenRefresh(BaseModel):
    refresh_token: str


# --- 登录接口 ---
@login.post("/login", summary="用户登录", response_model=Token)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    result = await auth_service.login(
        username=form_data.username,
        password=form_data.password
    )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


# --- 注册接口 ---
@login.post("/user", summary="用户新增", status_code=status.HTTP_201_CREATED)
async def user_create(user_in: UserCreate):
    """
    用户注册接口
    - 普通用户注册：无需提供 admin_register_key
    - 管理员注册：必须提供正确的 admin_register_key（在 .env 中配置）
    """
    result = await auth_service.register(
        username=user_in.username,
        password=user_in.password,
        nickname=user_in.nickname,
        email=user_in.email,
        admin_key=user_in.admin_register_key
    )

    if "error" in result:
        # 根据错误类型返回不同的状态码
        if "已存在" in result["error"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result["error"]
            )

    return result


# --- 刷新令牌接口 ---
@login.post("/refresh", summary="刷新访问令牌", response_model=Token)
async def refresh_token(refresh_request: TokenRefresh):
    """使用刷新令牌获取新的访问令牌和刷新令牌（令牌轮换）"""
    result = await auth_service.refresh_token(refresh_request.refresh_token)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"],
        )

    return result


# --- 登出接口 ---
@login.post("/logout", summary="用户登出")
async def logout(authorization: str = Header(None)):
    """登出接口，将 Token 加入黑名单"""
    return await auth_service.logout(authorization=authorization)