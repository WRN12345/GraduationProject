"""
@Time : 2025.12.9
@Author: wrn
@Des: hash加密与安全认证
"""
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist
from backend.core.config import settings
from backend.models.user import User
from backend.core.cache import get_redis_direct
from redis.asyncio import Redis
import uuid 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 密码处理 ---

def verify_password(plain_password: str, hashed_password: str) -> bool:


    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:

    password_bytes = password.encode('utf-8')[:72]
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

    # 生成唯一的 JWT ID（用于黑名单）
    jti = str(uuid.uuid4())

    # 写入过期时间、类型和 jti
    to_encode.update({"exp": expire, "type": "access", "jti": jti})

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

    # 生成唯一的 JWT ID（用于黑名单）
    jti = str(uuid.uuid4())

    # 写入过期时间、类型和 jti
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})

    # 生成 Token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> dict:
    """验证刷新令牌并返回 payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise JWTError("Not a refresh token")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Redis 黑名单管理 ---

async def add_token_to_blacklist(token: str, redis: Redis, expiry_seconds: int = None):
    """
    将 Token 添加到 Redis 黑名单
    :param token: JWT Token（纯 Token 字符串，不包含 "Bearer " 前缀）
    :param redis: Redis 客户端
    :param expiry_seconds: 黑名单过期时间（秒），默认为 Token 的剩余有效期
    """
    import logging

    # 验证 Token 格式
    if not token or not isinstance(token, str):
        raise ValueError("Token 不能为空")

    token = token.strip()

    # 移除可能的 "Bearer " 前缀
    if token.startswith("Bearer "):
        token = token[7:].strip()

    # JWT Token 应该有 2 个点（3 个部分）
    if token.count('.') != 2:
        raise ValueError(
            f"Token 格式无效：JWT 应该有 3 个部分（用 . 分隔），"
            f"但找到 {token.count('.') + 1} 个部分"
        )

    try:
        # 解码 Token 获取 jti 和过期时间
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            raise ValueError("Token 缺少 jti (JWT ID)")

        # 如果没有指定过期时间，使用 Token 的剩余有效期
        if expiry_seconds is None and exp:
            expiry_seconds = int(exp - datetime.now(timezone.utc).timestamp())

        # 确保 expiry_seconds 为正数
        if expiry_seconds is not None and expiry_seconds > 0:
            # 将 Token 添加到黑名单，key 为 token:blacklist:{jti}
            blacklist_key = f"token:blacklist:{jti}"
            await redis.setex(blacklist_key, expiry_seconds, "1")
            logging.info(f"Token (jti: {jti[:8]}...) 已添加到黑名单，有效期 {expiry_seconds} 秒")
        else:
            # Token 已过期，不需要添加到黑名单
            logging.warning(f"Token (jti: {jti[:8]}...) 已过期，不添加到黑名单")

    except JWTError as e:
        logging.error(f"Token 解码失败: {str(e)}, Token: {token[:50]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"无效的 Token: {str(e)}"
        )
    except ValueError as e:
        logging.error(f"Token 验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def is_token_blacklisted(token: str, redis: Redis) -> bool:
    """
    检查 Token 是否在黑名单中
    :param token: JWT Token
    :param redis: Redis 客户端
    :return: True 如果在黑名单中，False 否则
    """
    try:
        # 解码 Token 获取 jti
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
        jti = payload.get("jti")

        if not jti:
            # 没有 jti 的旧 Token，不在黑名单中
            return False

        # 检查黑名单
        blacklist_key = f"token:blacklist:{jti}"
        result = await redis.exists(blacklist_key)
        return result > 0

    except JWTError:
        # Token 格式错误，视为无效
        return True

# --- 依赖注入 ---

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_direct)
) -> User:
    """
    依赖项：校验 Token 并返回当前用户对象
    支持 Redis 黑名单检查
    Token 只解码一次，复用 payload
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 验证 Token 格式
    if not token or token.count('.') != 2:
        raise credentials_exception

    # 解码 Token（只解码一次）
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise credentials_exception

    # 检查 Redis 黑名单（使用已解码的 payload）
    if redis:
        try:
            is_blacklisted = await is_token_blacklisted(token, redis)
            if is_blacklisted:
                await redis.close()  # 关闭 Redis 连接
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token 已失效（已登出）",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except Exception as e:
            # Redis 检查失败，记录日志但不阻止请求（降级处理）
            import logging
            logging.warning(f"Redis 黑名单检查失败: {e}")

    # 获取用户 ID（使用已解码的 payload）
    user_id: str = payload.get("id")
    if user_id is None:
        await redis.close()  # 关闭 Redis 连接
        raise credentials_exception

    # 查询用户
    user = await User.get_or_none(id=user_id)
    await redis.close()  # 关闭 Redis 连接

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


async def get_current_user_with_token(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_direct)
) -> tuple[User, str]:
    """
    依赖项：返回当前用户和原始 Token
    用于需要同时使用用户信息和 Token 的场景（如登出）
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 验证 Token 格式
    if not token or token.count('.') != 2:
        raise credentials_exception

    # 解码 Token（只解码一次）
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise credentials_exception

    # 检查 Redis 黑名单
    if redis:
        try:
            is_blacklisted = await is_token_blacklisted(token, redis)
            if is_blacklisted:
                await redis.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token 已失效（已登出）",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except Exception as e:
            import logging
            logging.warning(f"Redis 黑名单检查失败: {e}")

    # 获取用户 ID
    user_id: str = payload.get("id")
    if user_id is None:
        await redis.close()
        raise credentials_exception

    # 查询用户
    user = await User.get_or_none(id=user_id)
    await redis.close()

    if user is None:
        raise credentials_exception

    # 检查用户是否被激活/冻结
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被冻结，无法访问"
        )

    # 返回用户和原始 Token
    return user, token