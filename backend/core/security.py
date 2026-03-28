"""
@Time : 2025.12.9
@Author: wrn
@Des: hash加密与安全认证
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from core.config import settings
from models.user import User

# 延迟导入以避免循环依赖（已移除黑名单服务）


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/login", auto_error=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 密码处理 ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated, hashed_password)

def get_password_hash(password: str) -> str:

    password_bytes = password.encode('utf-8')[:72]   #Bcrypt 算法本身只处理输入的前72个字节，若不截断，两个只有第73位不同的密码会被认为相同。
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)

# --- Token 处理 ---

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    # 优先使用传入的时间，否则使用配置文件的默认时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 写入过期时间和 payload
    to_encode.update({"exp": expire, "type": "access"})

    # 生成 Token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()

    # 优先使用传入的时间，否则使用配置文件的默认时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # 写入过期时间和 payload
    to_encode.update({"exp": expire, "type": "refresh"})

    # 生成 Token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> dict:
    """验证刷新令牌并返回 payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise JWTError("Not a refresh token")# 防止用 access_token 冒充 refresh_token
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- 依赖注入 ---

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    依赖项：校验 Token 并返回当前用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. 解码并验证 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # 2. 获取用户 ID（无状态验证）
        user_id: str = payload.get("id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        # Token 格式错误或签名不对
        raise credentials_exception


    user = await User.get_or_none(id=user_id)

    if user is None:
        raise credentials_exception

    # 检查用户是否被激活/冻结
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被冻结，无法访问"
        )

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    依赖项：验证当前用户是否为管理员
    用于需要管理员权限的接口
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问"
        )
    return current_user


async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[User]:
    """
    依赖项：可选认证，如果提供了 token 则验证，否则返回 None
    用于公开内容但支持用户信息的接口
    """
    if not token:
        return None

    try:
        # 解码 Token（无状态验证）
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # 获取用户 ID
        user_id: str = payload.get("id")

        if user_id is None:
            return None

    except JWTError:
        # Token 格式错误或签名不对
        return None

    user = await User.get_or_none(id=user_id)

    if user is None or not user.is_active:
        return None

    return user