# -*- coding:utf-8 -*-
"""
@Time : 2026.03.15
@Author: wrn
@Des: Business Logic Services - 按领域分类
"""

from .auth import (
    auth_service,
    token_blacklist_service,
    user_service,
)
from .content import (
    post_service,
    comment_service,
    vote_service,
    bookmark_service,
    community_service,
    membership_service,
    search_service,
)
from .infrastructure import (
    hot_rank_service,
    post_cache_service,
    comment_cache_service,
    minio_service,
    upload_service,
    attachment_service,
)

__all__ = [
    # Auth
    "auth_service",
    "token_blacklist_service",
    "user_service",
    # Content
    "post_service",
    "comment_service",
    "vote_service",
    "bookmark_service",
    "community_service",
    "membership_service",
    "search_service",
    # Infrastructure
    "hot_rank_service",
    "post_cache_service",
    "comment_cache_service",
    "minio_service",
    "upload_service",
    "attachment_service",
]
