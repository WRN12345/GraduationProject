"""
基础设施类服务
"""
from .redis_service import hot_rank_service, post_cache_service, comment_cache_service
from .minio_service import minio_service
from .upload_service import upload_service
from .attachment_service import attachment_service

__all__ = [
    "hot_rank_service",
    "post_cache_service",
    "comment_cache_service",
    "minio_service",
    "upload_service",
    "attachment_service",
]
