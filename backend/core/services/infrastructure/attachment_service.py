"""
附件访问服务 - 提供 presigned URL 和缓存
"""
from datetime import timedelta
from typing import Optional
from core.cache import get_redis
from core.services.infrastructure.minio_service import minio_service


class AttachmentService:
    """附件访问服务 - 提供 presigned URL 和缓存"""

    PRESIGNED_URL_TTL = 23 * 3600  # 23小时缓存（略小于24小时过期）
    CACHE_PREFIX = "attachment:presigned"

    @staticmethod
    def _get_cache_key(attachment_id: int) -> str:
        return f"{AttachmentService.CACHE_PREFIX}:{attachment_id}"

    async def get_presigned_url(
        self,
        attachment_id: int,
        file_url: str,
        use_cache: bool = True
    ) -> str:
        """
        获取附件的 presigned URL（带缓存）

        Args:
            attachment_id: 附件 ID
            file_url: 文件 URL
            use_cache: 是否使用缓存

        Returns:
            presigned URL
        """
        # 尝试从缓存获取
        if use_cache:
            redis = await get_redis().__anext__()
            try:
                cache_key = self._get_cache_key(attachment_id)
                cached_url = await redis.get(cache_key)
                if cached_url:
                    return cached_url
            finally:
                await redis.close()

        # 生成新的 presigned URL
        presigned_url = await minio_service.generate_presigned_url(
            file_url,
            expires=timedelta(hours=24)
        )

        # 存入缓存
        if use_cache:
            redis = await get_redis().__anext__()
            try:
                cache_key = self._get_cache_key(attachment_id)
                await redis.setex(
                    cache_key,
                    self.PRESIGNED_URL_TTL,
                    presigned_url
                )
            finally:
                await redis.close()

        return presigned_url

    async def batch_get_presigned_urls(
        self,
        attachments: list[dict],
        use_cache: bool = True
    ) -> dict[int, str]:
        """
        批量获取 presigned URLs

        Args:
            attachments: 附件列表 [{id, file_url}, ...]
            use_cache: 是否使用缓存

        Returns:
            {attachment_id: presigned_url} 字典
        """
        result = {}
        missed_attachments = []

        if use_cache:
            # 批量从缓存获取
            redis = await get_redis().__anext__()
            try:
                cache_keys = [
                    self._get_cache_key(a['id'])
                    for a in attachments
                ]
                cached_values = await redis.mget(cache_keys)

                # 分离命中和未命中的
                for i, attachment in enumerate(attachments):
                    attachment_id = attachment['id']
                    cached_url = cached_values[i]
                    if cached_url:
                        result[attachment_id] = cached_url
                    else:
                        missed_attachments.append(attachment)
            finally:
                await redis.close()
        else:
            missed_attachments = attachments

        # 为未命中的生成新的 presigned URLs
        if missed_attachments:
            redis = await get_redis().__anext__() if use_cache else None
            try:
                pipe = redis.pipeline() if redis else None

                for attachment in missed_attachments:
                    attachment_id = attachment['id']
                    file_url = attachment['file_url']

                    presigned_url = await minio_service.generate_presigned_url(
                        file_url,
                        expires=timedelta(hours=24)
                    )

                    result[attachment_id] = presigned_url

                    # 批量写入缓存
                    if pipe:
                        cache_key = self._get_cache_key(attachment_id)
                        pipe.setex(
                            cache_key,
                            self.PRESIGNED_URL_TTL,
                            presigned_url
                        )

                if pipe:
                    await pipe.execute()
            finally:
                if redis:
                    await redis.close()

        return result

    async def invalidate_cache(self, attachment_id: int):
        """失效附件缓存（删除/更新时调用）"""
        redis = await get_redis().__anext__()
        try:
            cache_key = self._get_cache_key(attachment_id)
            await redis.delete(cache_key)
        finally:
            await redis.close()


# 全局单例
attachment_service = AttachmentService()
