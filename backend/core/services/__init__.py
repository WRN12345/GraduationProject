# -*- coding:utf-8 -*-
"""
@Time : 2026.03.15
@Author: wrn
@Des: Business Logic Services - 按领域分类
"""

from .auth import (
    auth_service,
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
    hot_content_service,
    draft_service,
)
from .infrastructure import (
    hot_rank_service,
    post_cache_service,
    comment_cache_service,
    rustfs_service,
    upload_service,
    attachment_service,
)
from .admin import (
    admin_service,
)
