"""
@Created on : 2026/3/15
@Author: wrn
@Des: 认证服务 - 登录、注册、Token 管理
"""
from typing import Optional
from models.user import User
from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_refresh_token
from core.config import settings
from tortoise.expressions import Q
from core.services.auth.token_blacklist_service import token_blacklist_service
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务 - 登录、注册、Token 管理"""

    async def login(
        self,
        username: str,
        password: str
    ) -> dict:
        """
        用户登录

        Args:
            username: 用户名或邮箱
            password: 密码

        Returns:
            dict: 包含 token 的登录响应

        Raises:
            Returns {"error": "..."} on failure
        """
        # 1. 查询用户（支持用户名或邮箱登录）
        user = await User.get_or_none(
            Q(username=username) | Q(email=username)
        )

        # 2. 统一处理认证失败 (防止用户名枚举攻击)
        if not user or not verify_password(password, user.password):
            return {"error": "用户名或密码错误"}

        # 3. 生成并返回 Token
        access_token = create_access_token(data={
            "sub": user.username,
            "id": user.id,
            "is_superuser": user.is_superuser
        })
        refresh_token = create_refresh_token(data={
            "sub": user.username,
            "id": user.id
        })

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "is_superuser": user.is_superuser,
            "user_id": user.id
        }

    async def register(
        self,
        username: str,
        password: str,
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        admin_key: Optional[str] = None
    ) -> dict:
        """
        用户注册

        Args:
            username: 用户名
            password: 密码
            nickname: 昵称
            email: 邮箱
            admin_key: 管理员注册密钥（可选）

        Returns:
            dict: 注册结果

        Raises:
            Returns {"error": "..."} on failure
        """
        # 1. 检查用户是否已存在
        exist_user = await User.get_or_none(username=username)
        if exist_user:
            return {"error": "用户名已存在"}

        # 2. 判断是否为管理员注册
        is_superuser = False
        if admin_key:
            # 验证管理员注册密钥（从环境变量读取）
            if hasattr(settings, 'ADMIN_REGISTER_KEY') and admin_key == settings.ADMIN_REGISTER_KEY:
                is_superuser = True
            else:
                return {"error": "管理员注册密钥无效，无法注册为管理员"}

        # 3. 创建用户对象
        user_obj = User(
            username=username,
            password=get_password_hash(password),
            nickname=nickname,
            email=email,
            is_superuser=is_superuser
        )

        # 4. 保存到数据库
        await user_obj.save()

        return {
            "code": 200,
            "msg": "用户创建成功",
            "is_superuser": is_superuser,
            "username": user_obj.username
        }

    async def refresh_token(
        self,
        refresh_token: str
    ) -> dict:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            dict: 包含新 token 的响应

        Raises:
            Returns {"error": "..."} on failure
        """
        # 验证刷新令牌
        payload = verify_refresh_token(refresh_token)

        # 获取用户 ID
        user_id = payload.get("id")
        if not user_id:
            return {"error": "无效的刷新令牌"}

        # 验证用户是否存在
        user = await User.get_or_none(id=user_id)
        if not user:
            return {"error": "用户不存在"}

        # 生成新的访问令牌和刷新令牌（令牌轮换）
        access_token = create_access_token(data={
            "sub": user.username,
            "id": user.id,
            "is_superuser": user.is_superuser
        })
        new_refresh_token = create_refresh_token(data={
            "sub": user.username,
            "id": user.id
        })

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "is_superuser": user.is_superuser,
            "user_id": user.id
        }

    async def logout(self, authorization: str = None) -> dict:
        """
        用户登出 - 将 Token 加入黑名单

        Args:
            authorization: Authorization 请求头值

        Returns:
            dict: 登出结果
        """
        try:
            # 提取 Bearer Token
            if not authorization or not authorization.startswith("Bearer "):
                return {
                    "message": "登出成功",
                    "warning": "未找到有效的 Token"
                }

            token = authorization.split(" ")[1]

            # 添加到黑名单
            result = await token_blacklist_service.add_to_blacklist(token)

            if "error" in result:
                # Token 无效或已过期，但仍返回成功（客户端会清除本地 Token）
                return {
                    "message": "登出成功",
                    "warning": result["error"]
                }

            return {
                "message": "登出成功，Token 已失效",
                "details": {
                    "ttl": result.get("ttl"),
                    "exp": result.get("exp")
                }
            }

        except Exception as e:
            # 即使出错也返回成功（确保客户端能清除 Token）
            return {
                "message": "登出成功",
                "warning": f"黑名单操作异常: {str(e)}"
            }


# 导出服务实例
auth_service = AuthService()

__all__ = ["AuthService", "auth_service"]
