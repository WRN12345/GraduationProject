"""
@Created on : 2026/4/3
@Author: wrn
@Des: 管理员数据统计与用户管理服务 - 控制面板统计 + 用户列表 + 用户管理
"""
from typing import Optional
from datetime import datetime, timezone
from tortoise import transactions
from tortoise.expressions import F
from models.user import User
from models.post import Post
from models.comment import Comment
from models.community import Community
from models.audit_log import ActionType, TargetType
from core.audit import create_audit_log
from core.services.admin.content_management_service import AdminErrorCode
import logging

logger = logging.getLogger(__name__)


class StatsService:
    """管理员数据统计与用户管理服务"""

    async def get_dashboard_stats(self) -> dict:
        """
        获取控制面板统计数据

        Returns:
            dict: 统计数据
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 总量统计
        total_users = await User.all().count()
        total_posts = await Post.all().count()
        total_comments = await Comment.all().count()
        total_communities = await Community.all().count()

        # 今日新增
        today_new_users = await User.filter(created_at__gte=today_start).count()
        today_new_posts = await Post.filter(created_at__gte=today_start).count()
        today_new_comments = await Comment.filter(created_at__gte=today_start).count()

        # 管理统计
        deleted_posts = await Post.filter(deleted_at__isnull=False).count()
        deleted_comments = await Comment.filter(deleted_at__isnull=False).count()
        admin_users = await User.filter(is_superuser=True).count()
        banned_users = await User.filter(is_active=False).count()

        return {
            "total_users": total_users,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_communities": total_communities,
            "today_new_users": today_new_users,
            "today_new_posts": today_new_posts,
            "today_new_comments": today_new_comments,
            "deleted_posts": deleted_posts,
            "deleted_comments": deleted_comments,
            "admin_users": admin_users,
            "banned_users": banned_users,
        }

    async def get_all_users(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        search: Optional[str] = None
    ) -> dict:
        """
        获取所有用户列表（支持筛选和搜索）

        Args:
            page: 页码
            page_size: 每页数量
            is_active: 是否激活筛选
            is_superuser: 是否管理员筛选
            search: 用户名/昵称搜索

        Returns:
            dict: 分页用户列表
        """
        from tortoise.expressions import Q

        query = User.all().order_by("-created_at")

        # 可选筛选条件
        if is_active is not None:
            query = query.filter(is_active=is_active)
        if is_superuser is not None:
            query = query.filter(is_superuser=is_superuser)
        if search:
            query = query.filter(
                Q(username__icontains=search) | Q(nickname__icontains=search)
            )

        total = await query.count()
        skip = (page - 1) * page_size
        users = await query.offset(skip).limit(page_size)

        items = []
        for u in users:
            items.append({
                "id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "email": u.email,
                "avatar": u.avatar,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "karma": u.karma,
                "post_count": u.post_count,
                "comment_count": u.comment_count,
                "created_at": u.created_at,
                "last_login": u.last_login,
            })

        has_more = skip + page_size < total

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": has_more,
        }

    async def get_user_detail(self, user_id: int) -> dict:
        """
        获取用户详细信息（管理员视角）

        Args:
            user_id: 用户 ID

        Returns:
            dict: 用户详细信息
        """
        user = await User.get_or_none(id=user_id)

        if not user:
            return {"error": "用户不存在", "code": AdminErrorCode.NOT_FOUND}

        # 统计用户帖子数和评论数
        post_count = await Post.filter(author_id=user_id).count()
        comment_count = await Comment.filter(author_id=user_id).count()
        deleted_posts = await Post.filter(author_id=user_id, deleted_at__isnull=False).count()
        deleted_comments = await Comment.filter(author_id=user_id, deleted_at__isnull=False).count()

        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "karma": user.karma,
            "bio": user.bio,
            "post_count": post_count,
            "comment_count": comment_count,
            "deleted_posts": deleted_posts,
            "deleted_comments": deleted_comments,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }

    async def ban_user(
        self,
        user_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """
        冻结用户（设置 is_active=False）

        Args:
            user_id: 目标用户 ID
            admin_user: 执行操作的管理员
            reason: 冻结原因

        Returns:
            dict: 操作结果
        """
        target_user = await User.get_or_none(id=user_id)

        if not target_user:
            return {"error": "用户不存在", "code": AdminErrorCode.NOT_FOUND}

        if target_user.is_superuser:
            return {"error": "无法冻结管理员账户", "code": AdminErrorCode.FORBIDDEN}

        if not target_user.is_active:
            return {"error": "用户已被冻结", "code": AdminErrorCode.ALREADY_DELETED}

        async with transactions.in_transaction():
            await User.filter(id=user_id).update(is_active=False)

            # 记录审计日志
            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.USER,
                target_id=user_id,
                action_type=ActionType.BAN_USER,
                reason=reason,
                metadata={
                    "username": target_user.username,
                    "nickname": target_user.nickname,
                }
            )

        logger.warning(
            f"Admin {admin_user.username}(id={admin_user.id}) banned user "
            f"{target_user.username}(id={user_id}), reason: {reason}"
        )

        return {"message": "用户已冻结", "target_id": user_id}

    async def unban_user(
        self,
        user_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """
        解冻用户（设置 is_active=True）

        Args:
            user_id: 目标用户 ID
            admin_user: 执行操作的管理员
            reason: 解冻原因

        Returns:
            dict: 操作结果
        """
        target_user = await User.get_or_none(id=user_id)

        if not target_user:
            return {"error": "用户不存在", "code": AdminErrorCode.NOT_FOUND}

        if target_user.is_active:
            return {"error": "用户未被冻结，无需解冻", "code": AdminErrorCode.NOT_DELETED}

        async with transactions.in_transaction():
            await User.filter(id=user_id).update(is_active=True)

            # 记录审计日志
            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.USER,
                target_id=user_id,
                action_type=ActionType.UNBAN_USER,
                reason=reason,
                metadata={
                    "username": target_user.username,
                    "nickname": target_user.nickname,
                }
            )

        logger.info(
            f"Admin {admin_user.username}(id={admin_user.id}) unbanned user "
            f"{target_user.username}(id={user_id}), reason: {reason}"
        )

        return {"message": "用户已解冻", "target_id": user_id}


# 导出服务实例
stats_service = StatsService()

__all__ = ["StatsService", "stats_service"]
