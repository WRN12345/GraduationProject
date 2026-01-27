"""
@Created on : 2025/12/8
@Author: wrn
@Des: 登录注册路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from backend.models.user import User
from backend.schemas import UserCreate
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user,
    get_current_user_with_token
)

login = APIRouter(tags=["认证相关"])

# OAuth2 密码模式（用于从 Header 获取 Token）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/login")

# ---  Token 响应 ---
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
    # 1. 查询用户
    user = await User.get_or_none(username=form_data.username)
    
    # 2. 统一处理认证失败 (防止用户名枚举攻击)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 生成并返回 Token
    access_token = create_access_token(data={"sub": user.username, "id": user.id, "is_superuser": user.is_superuser})
    refresh_token = create_refresh_token(data={"sub": user.username, "id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "is_superuser": user.is_superuser,
        "user_id": user.id
    }

# --- 注册接口 ---
@login.post("/user", summary="用户新增", status_code=status.HTTP_201_CREATED)

async def user_create(user_in: UserCreate, admin_key: str = None):
    """
    用户注册接口
    - 普通用户注册：无需提供 admin_key
    - 管理员注册：必须提供正确的 admin_key（在 .env 中配置）
    """
    # 1. 检查用户是否已存在
    exist_user = await User.get_or_none(username=user_in.username)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 2. 判断是否为管理员注册
    is_superuser = False
    if admin_key:
        # 验证管理员注册密钥（从环境变量读取）
        from backend.core.config import settings
        if hasattr(settings, 'ADMIN_REGISTER_KEY') and admin_key == settings.ADMIN_REGISTER_KEY:
            is_superuser = True
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理员注册密钥无效，无法注册为管理员"
            )

    # 3. 创建用户对象
    user_obj = User(
        username=user_in.username,
        password=get_password_hash(user_in.password),
        nickname=user_in.nickname,
        email=user_in.email,
        is_superuser=is_superuser  # 设置管理员权限
    )

    # 4. 保存到数据库
    await user_obj.save()

    # 5. 返回结果
    return {
        "code": 200,
        "msg": "用户创建成功",
        "is_superuser": is_superuser,
        "username": user_obj.username
    }

# --- 刷新令牌接口 ---
@login.post("/refresh", summary="刷新访问令牌", response_model=Token)

async def refresh_token(refresh_request: TokenRefresh):
    """使用刷新令牌获取新的访问令牌和刷新令牌（令牌轮换）"""
    # 验证刷新令牌
    payload = verify_refresh_token(refresh_request.refresh_token)

    # 获取用户 ID
    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
        )

    # 验证用户是否存在
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 生成新的访问令牌和刷新令牌（令牌轮换）
    access_token = create_access_token(data={"sub": user.username, "id": user.id, "is_superuser": user.is_superuser})
    new_refresh_token = create_refresh_token(data={"sub": user.username, "id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "is_superuser": user.is_superuser,
        "user_id": user.id
    }

# --- 登出接口 ---
@login.post("/logout", summary="用户登出")
async def logout(
    current_user_token: tuple[User, str] = Depends(get_current_user_with_token)
):
    """
    服务端登出接口（使用 Redis 黑名单）

    只需从 Authorization Header 传入 Token，自动验证并添加到黑名单

    ## 请求方式
    - **Header**: `Authorization: Bearer <access_token>`
    - **Body**: 无需请求体
    """
    from backend.core.cache import get_redis_direct
    from backend.core.security import add_token_to_blacklist
    import logging

    # 解包：获取用户和原始 Token
    current_user, access_token = current_user_token

    try:
        # 获取 Redis 客户端
        redis = await get_redis_direct()

        # 将 Token 添加到黑名单
        await add_token_to_blacklist(access_token, redis)

        # 关闭 Redis 连接
        await redis.close()

        logging.info(f"用户 {current_user.username} (ID: {current_user.id}) 已登出")

    except Exception as e:
        # Redis 操作失败，记录日志
        logging.error(f"用户 {current_user.username} 登出时添加黑名单失败: {e}")
        # 即使 Redis 失败，也返回成功（客户端删除令牌即可）

    return {
        "message": "登出成功",
        "username": current_user.username,
        "detail": "Token 已失效，请删除客户端存储的令牌"
    }