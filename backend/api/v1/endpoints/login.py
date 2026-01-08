"""
@Created on : 2025/12/8
@Author: wrn
@Des: 登录注册路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from backend.models.user import User
from backend.schemas import UserCreate 
from backend.core.security import verify_password, get_password_hash, create_access_token

login = APIRouter(tags=["认证相关"])

# ---  Token 响应 ---
class Token(BaseModel):
    access_token: str
    token_type: str

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
    return {
        "access_token": create_access_token(data={"sub": user.username, "id": user.id}),
        "token_type": "bearer"
    }

# --- 注册接口 ---
@login.post("/user", summary="用户新增", status_code=status.HTTP_201_CREATED)

async def user_create(user_in: UserCreate):
    # 1. 检查用户是否已存在
    exist_user = await User.get_or_none(username=user_in.username)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 2. 创建用户对象
    
    user_obj = User(
        username=user_in.username,
        password=get_password_hash(user_in.password),
        nickname=user_in.nickname,
        email=user_in.email
    )

    # 3. 保存到数据库
    await user_obj.save()
    
    # 4. 返回结果
    return {"code": 200, "msg": "用户创建成功"}