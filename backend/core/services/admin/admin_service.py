"""
@Created on : 2026/4/3
@Author: wrn
@Des: 超级管理员门面服务 - 统一入口，委托给专业子服务
"""
from typing import Optional

from core.services.admin.stats_service import stats_service
from core.services.admin.content_management_service import content_management_service
from core.services.admin.audit_service import audit_service
from models.user import User

import logging

logger = logging.getLogger(__name__)


class AdminService:
    """
    超级管理员门面服务（Facade Pattern）

    作为统一入口，将请求委托给专业子服务：
    - stats_service: 数据统计 + 用户管理
    - content_management_service: 帖子/评论管理
    - audit_service: 审计日志查询
    """

    # ========== 数据统计（委托给 stats_service）==========

    async def get_dashboard_stats(self) -> dict:
        """获取控制面板统计数据"""
        return await stats_service.get_dashboard_stats()

    # ========== 用户管理（委托给 stats_service）==========

    async def get_all_users(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        search: Optional[str] = None
    ) -> dict:
        """获取所有用户列表（支持筛选和搜索）"""
        return await stats_service.get_all_users(
            page=page,
            page_size=page_size,
            is_active=is_active,
            is_superuser=is_superuser,
            search=search
        )

    async def get_user_detail(self, user_id: int) -> dict:
        """获取用户详细信息（管理员视角）"""
        return await stats_service.get_user_detail(user_id)

    async def ban_user(
        self,
        user_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """冻结用户"""
        return await stats_service.ban_user(user_id, admin_user, reason)

    async def unban_user(
        self,
        user_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """解冻用户"""
        return await stats_service.unban_user(user_id, admin_user, reason)

    # ========== 帖子管理（委托给 content_management_service）==========

    async def get_all_posts(
        self,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False
    ) -> dict:
        """获取所有帖子列表（含已删除）"""
        return await content_management_service.get_all_posts(
            page=page,
            page_size=page_size,
            include_deleted=include_deleted
        )

    async def delete_post(
        self,
        post_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员软删除帖子"""
        return await content_management_service.delete_post(post_id, admin_user, reason)

    async def restore_post(
        self,
        post_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员恢复软删除的帖子"""
        return await content_management_service.restore_post(post_id, admin_user, reason)

    async def hard_delete_post(
        self,
        post_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员硬删除帖子（永久删除，不可逆）"""
        return await content_management_service.hard_delete_post(post_id, admin_user, reason)

    # ========== 评论管理（委托给 content_management_service）==========

    async def get_all_comments(
        self,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False
    ) -> dict:
        """获取所有评论列表（含已删除）"""
        return await content_management_service.get_all_comments(
            page=page,
            page_size=page_size,
            include_deleted=include_deleted
        )

    async def delete_comment(
        self,
        comment_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员软删除评论"""
        return await content_management_service.delete_comment(comment_id, admin_user, reason)

    async def restore_comment(
        self,
        comment_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员恢复评论"""
        return await content_management_service.restore_comment(comment_id, admin_user, reason)

    async def hard_delete_comment(
        self,
        comment_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员硬删除评论（永久删除，不可逆）"""
        return await content_management_service.hard_delete_comment(comment_id, admin_user, reason)

    # ========== 审计日志（委托给 audit_service）==========

    async def get_admin_audit_logs(
        self,
        admin_id: int,
        page: int = 1,
        page_size: int = 20,
        action_type: Optional[int] = None,
        target_type: Optional[int] = None
    ) -> dict:
        """获取指定管理员的操作日志"""
        return await audit_service.get_admin_audit_logs(
            admin_id=admin_id,
            page=page,
            page_size=page_size,
            action_type=action_type,
            target_type=target_type
        )

    async def get_all_audit_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        action_type: Optional[int] = None,
        target_type: Optional[int] = None,
        actor_id: Optional[int] = None
    ) -> dict:
        """获取所有审计日志（支持多维度筛选）"""
        return await audit_service.get_all_audit_logs(
            page=page,
            page_size=page_size,
            action_type=action_type,
            target_type=target_type,
            actor_id=actor_id
        )


# 导出服务实例
admin_service = AdminService()

__all__ = ["AdminService", "admin_service"]
