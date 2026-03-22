"""
Token 黑名单服务
用于实现安全退出登录功能，将已登出的 Token 加入 Redis 黑名单
"""
import redis.asyncio as redis
from typing import Optional
from core.config import settings
import jwt
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class TokenBlacklistService:
    """Token 黑名单服务"""

    BLACKLIST_PREFIX = "blacklist:token"

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """获取 Redis 连接"""
        if self._redis is None:
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
        return self._redis

    def _get_blacklist_key(self, token: str) -> str:
        """生成黑名单键"""
        return f"{self.BLACKLIST_PREFIX}:{token}"

    async def add_to_blacklist(self, token: str) -> dict:
        """
        将 Token 添加到黑名单

        Args:
            token: JWT Token 字符串

        Returns:
            dict: 操作结果
        """
        try:
            # 解析 Token 获取过期时间
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_signature": True}  # 验证签名确保 Token 有效
            )

            exp = payload.get("exp")
            if exp is None:
                return {"error": "Token 无过期时间"}

            # 计算剩余有效期（秒）
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(0, exp - now)

            # 如果已过期，无需添加到黑名单
            if ttl <= 0:
                logger.info(f"Token 已过期，无需加入黑名单: {token[:20]}...")
                return {"message": "Token 已过期，无需加入黑名单"}

            # 存入 Redis，设置 TTL
            r = await self._get_redis()
            key = self._get_blacklist_key(token)
            await r.setex(key, ttl, "1")  # 值为 "1" 表示存在

            logger.info(f"Token 已加入黑名单，TTL: {ttl}秒")

            return {
                "message": "Token 已加入黑名单",
                "ttl": ttl,
                "exp": exp
            }

        except jwt.ExpiredSignatureError:
            logger.warning(f"尝试加入黑名单的 Token 已过期")
            return {"error": "Token 已过期"}
        except jwt.InvalidTokenError as e:
            logger.warning(f"尝试加入黑名单的 Token 无效: {str(e)}")
            return {"error": f"Token 无效: {str(e)}"}
        except Exception as e:
            logger.error(f"添加 Token 到黑名单失败: {str(e)}")
            return {"error": f"添加黑名单失败: {str(e)}"}

    async def is_blacklisted(self, token: str) -> bool:
        """
        检查 Token 是否在黑名单中

        Args:
            token: JWT Token 字符串

        Returns:
            bool: True 表示在黑名单中
        """
        try:
            r = await self._get_redis()
            key = self._get_blacklist_key(token)
            result = await r.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"检查黑名单失败: {str(e)}")
            # Redis 异常时，为了安全起见，不阻止请求
            return False

    async def close(self):
        """关闭 Redis 连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None


# 单例导出
token_blacklist_service = TokenBlacklistService()

__all__ = ["TokenBlacklistService", "token_blacklist_service"]
