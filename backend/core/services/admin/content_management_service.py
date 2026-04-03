"""
@Created on : 2026/4/3
@Author: wrn
@Des: 管理员内容管理服务 - 帖子/评论的软删除、恢复、硬删除
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import status
from tortoise import transactions
from tortoise.expressions import F
from tortoise.functions import Count as Count
from models.user import User
from models.post import Post
from models.comment import Comment
from models.community import Community
from models.audit_log import ActionType, TargetType
from core.audit import create_audit_log
import logging

logger = logging.getLogger(__name__)


# 管理员操作错误码常量
class AdminErrorCode:
    NOT_FOUND = "NOT_FOUND"
    ALREADY_DELETED = "ALREADY_DELETED"
    NOT_DELETED = "NOT_DELETED"
    FORBIDDEN = "FORBIDDEN"


# 错误码到 HTTP 状态码映射
ERROR_STATUS_MAP = {
    AdminErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    AdminErrorCode.ALREADY_DELETED: status.HTTP_400_BAD_REQUEST,
    AdminErrorCode.NOT_DELETED: status.HTTP_400_BAD_REQUEST,
    AdminErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
}


class ContentManagementService:
    """管理员内容管理服务 - 帖子/评论的管理"""

    async def get_all_posts(
        self,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False
    ) -> dict:
        """获取所有帖子列表（含已删除）"""
        query = Post.all().order_by("-created_at")
        query = query.prefetch_related('author', 'community')

        if not include_deleted:
            query = query.filter(deleted_at__isnull=True)

        total = await query.count()
        skip = (page - 1) * page_size
        # 使用 annotate 批量获取评论数，避免 N+1 查询
        posts = await query.annotate(
            comment_count_db=Count('comments')
        ).offset(skip).limit(page_size)

        items = []
        for post in posts:
            author_data = None
            if post.author:
                author_data = {
                    "id": post.author.id,
                    "username": post.author.username,
                    "avatar": post.author.avatar,
                }

            community_data = None
            if post.community:
                community_data = {
                    "id": post.community.id,
                    "name": post.community.name,
                }

            post_dict = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "community_id": post.community_id,
                "author_id": post.author_id,
                "author": author_data,
                "community": community_data,
                "upvotes": post.upvotes,
                "downvotes": post.downvotes,
                "score": post.score,
                "hot_rank": post.hot_rank,
                "is_locked": post.is_locked,
                "is_highlighted": post.is_highlighted,
                "is_pinned": post.is_pinned,
                "is_edited": post.is_edited,
                "deleted_at": post.deleted_at,
                "deleted_by_id": post.deleted_by_id,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "comment_count": post.comment_count_db,
            }
            items.append(post_dict)

        has_more = skip + page_size < total

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": has_more,
        }

    async def get_all_comments(
        self,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False
    ) -> dict:
        """获取所有评论列表（含已删除）"""
        query = Comment.all().order_by("-created_at")
        query = query.select_related('author')

        if not include_deleted:
            query = query.filter(deleted_at__isnull=True)

        total = await query.count()
        skip = (page - 1) * page_size
        comments = await query.offset(skip).limit(page_size)

        items = []
        for comment in comments:
            author_data = None
            if comment.author:
                author_data = {
                    "id": comment.author.id,
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                }

            comment_dict = {
                "id": comment.id,
                "content": comment.content,
                "post_id": comment.post_id,
                "author_id": comment.author_id,
                "author": author_data,
                "parent_id": comment.parent_id,
                "upvotes": comment.upvotes,
                "downvotes": comment.downvotes,
                "score": comment.score,
                "is_edited": comment.is_edited,
                "deleted_at": comment.deleted_at,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            }
            items.append(comment_dict)

        has_more = skip + page_size < total

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": has_more,
        }

    async def delete_post(
        self,
        post_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员软删除帖子"""
        post = await Post.get_or_none(id=post_id)

        if not post:
            return {"error": "帖子不存在", "code": AdminErrorCode.NOT_FOUND}

        if post.deleted_at:
            return {"error": "帖子已被删除", "code": AdminErrorCode.ALREADY_DELETED}

        async with transactions.in_transaction():
            await Post.filter(id=post_id).update(
                deleted_at=datetime.now(timezone.utc),
                deleted_by_id=admin_user.id
            )

            await Community.filter(id=post.community_id).update(
                post_count=F('post_count') - 1
            )

            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.POST,
                target_id=post_id,
                action_type=ActionType.ADMIN_DELETE_POST,
                reason=reason,
                metadata={"post_title": post.title, "original_author_id": post.author_id}
            )

        return {"message": "管理员删除帖子成功", "target_id": post_id}

    async def restore_post(
        self,
        post_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员恢复软删除的帖子"""
        post = await Post.get_or_none(id=post_id)

        if not post:
            return {"error": "帖子不存在", "code": AdminErrorCode.NOT_FOUND}

        if not post.deleted_at:
            return {"error": "帖子未被删除，无需恢复", "code": AdminErrorCode.NOT_DELETED}

        async with transactions.in_transaction():
            await Post.filter(id=post_id).update(
                deleted_at=None,
                deleted_by_id=None
            )

            await Community.filter(id=post.community_id).update(
                post_count=F('post_count') + 1
            )

            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.POST,
                target_id=post_id,
                action_type=ActionType.ADMIN_RESTORE_POST,
                reason=reason,
                metadata={"post_title": post.title, "original_author_id": post.author_id}
            )

        return {"message": "管理员恢复帖子成功", "target_id": post_id}

    async def hard_delete_post(
        self,
        post_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员硬删除帖子（永久删除，不可逆）"""
        post = await Post.get_or_none(id=post_id)

        if not post:
            return {"error": "帖子不存在", "code": AdminErrorCode.NOT_FOUND}

        # 先保存审计所需的元数据（删除后无法再读取）
        audit_metadata = {
            "post_title": post.title,
            "original_author_id": post.author_id,
            "community_id": post.community_id,
            "hard_deleted_at": datetime.now(timezone.utc).isoformat()
        }

        async with transactions.in_transaction():
            # 更新社区帖子计数（仅在帖子未被软删除时）
            if not post.deleted_at:
                await Community.filter(id=post.community_id).update(
                    post_count=F('post_count') - 1
                )

            # 删除帖子下的所有评论和帖子本身
            await Comment.filter(post_id=post_id).delete()
            await Post.filter(id=post_id).delete()

            # 在同一事务中记录审计日志
            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.POST,
                target_id=post_id,
                action_type=ActionType.ADMIN_HARD_DELETE_POST,
                reason=reason,
                metadata=audit_metadata
            )

        logger.warning(
            f"Admin {admin_user.username}(id={admin_user.id}) hard deleted post "
            f"{post_id}(title={post.title!r}), reason: {reason}"
        )

        return {"message": "管理员硬删除帖子成功（不可逆）", "target_id": post_id}

    async def _get_all_descendant_comment_ids(self, comment_id: int) -> list[int]:
        """
        递归收集评论的所有后代评论 ID（广度优先遍历）

        Args:
            comment_id: 根评论 ID

        Returns:
            list[int]: 所有后代评论的 ID 列表（不含根评论自身）
        """
        all_ids = []
        queue = [comment_id]
        while queue:
            current_id = queue.pop(0)
            children = await Comment.filter(parent_id=current_id).values_list('id', flat=True)
            all_ids.extend(children)
            queue.extend(children)
        return all_ids

    async def delete_comment(
        self,
        comment_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员软删除评论"""
        comment = await Comment.get_or_none(id=comment_id)

        if not comment:
            return {"error": "评论不存在", "code": AdminErrorCode.NOT_FOUND}

        if comment.deleted_at:
            return {"error": "评论已被删除", "code": AdminErrorCode.ALREADY_DELETED}

        async with transactions.in_transaction():
            await Comment.filter(id=comment_id).update(
                deleted_at=datetime.now(timezone.utc)
            )

            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.COMMENT,
                target_id=comment_id,
                action_type=ActionType.ADMIN_DELETE_COMMENT,
                reason=reason,
                metadata={
                    "post_id": comment.post_id,
                    "original_author_id": comment.author_id,
                    "content_preview": comment.content[:100] if comment.content else ""
                }
            )

        return {"message": "管理员删除评论成功", "target_id": comment_id}

    async def restore_comment(
        self,
        comment_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员恢复评论"""
        comment = await Comment.get_or_none(id=comment_id)

        if not comment:
            return {"error": "评论不存在", "code": AdminErrorCode.NOT_FOUND}

        if not comment.deleted_at:
            return {"error": "评论未被删除，无需恢复", "code": AdminErrorCode.NOT_DELETED}

        async with transactions.in_transaction():
            await Comment.filter(id=comment_id).update(deleted_at=None)

            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.COMMENT,
                target_id=comment_id,
                action_type=ActionType.ADMIN_RESTORE_COMMENT,
                reason=reason,
                metadata={
                    "post_id": comment.post_id,
                    "original_author_id": comment.author_id
                }
            )

        return {"message": "管理员恢复评论成功", "target_id": comment_id}

    async def hard_delete_comment(
        self,
        comment_id: int,
        admin_user: User,
        reason: Optional[str] = None
    ) -> dict:
        """管理员硬删除评论（永久删除，不可逆，递归删除所有后代评论）"""
        comment = await Comment.get_or_none(id=comment_id)

        if not comment:
            return {"error": "评论不存在", "code": AdminErrorCode.NOT_FOUND}

        # 先保存审计所需的元数据（删除后无法再读取）
        audit_metadata = {
            "post_id": comment.post_id,
            "original_author_id": comment.author_id,
            "content_preview": comment.content[:100] if comment.content else "",
            "hard_deleted_at": datetime.now(timezone.utc).isoformat()
        }

        # 递归收集所有后代评论 ID
        descendant_ids = await self._get_all_descendant_comment_ids(comment_id)

        async with transactions.in_transaction():
            # 先删除所有后代评论，再删除目标评论
            if descendant_ids:
                await Comment.filter(id__in=descendant_ids).delete()
            await Comment.filter(id=comment_id).delete()

            # 在同一事务中记录审计日志
            await create_audit_log(
                actor=admin_user,
                target_type=TargetType.COMMENT,
                target_id=comment_id,
                action_type=ActionType.ADMIN_HARD_DELETE_COMMENT,
                reason=reason,
                metadata=audit_metadata
            )

        logger.warning(
            f"Admin {admin_user.username}(id={admin_user.id}) hard deleted comment "
            f"{comment_id} and {len(descendant_ids)} descendant(s), reason: {reason}"
        )

        return {"message": "管理员硬删除评论成功（不可逆）", "target_id": comment_id}


# 导出服务实例
content_management_service = ContentManagementService()

__all__ = ["ContentManagementService", "content_management_service"]
