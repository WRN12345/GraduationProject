"""
@Created on : 2026/3/15
@Author: wrn
@Des: 帖子服务 - 帖子 CRUD + Redis 缓存 + 热度计算
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from redis.asyncio import Redis
from tortoise.expressions import F
from models.user import User
from models.community import Community
from models.post_attachment import PostAttachment
from models.comment import Comment
from models import post as models
from core.services.content.bookmark_service import bookmark_service
from core.services.content.vote_service import vote_service
from core.services.infrastructure.redis_service import hot_rank_service, post_cache_service
from core.services.infrastructure.rustfs_service import rustfs_service
from core.cache import get_redis
from schemas import post as schemas
from tortoise import transactions
from models.audit_log import ActionType, TargetType
from core.audit import create_audit_log
import logging

logger = logging.getLogger(__name__)


class PostService:
    """帖子服务 - Redis 缓存 + 热度计算 + 用户状态"""

    async def get_post_detail(
        self,
        redis: Redis,
        post_id: int,
        current_user: Optional[User] = None
    ) -> dict:
        """
        获取帖子详情（含用户状态）

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            current_user: 当前用户（可选）

        Returns:
            dict: 帖子详情

        Raises:
            Returns {"error": "..."} on failure
        """
        post = await models.Post.get_or_none(
            id=post_id
        ).select_related('author', 'community').prefetch_related('attachments')

        if not post:
            return {"error": "帖子不存在"}

        # 增加浏览计数并更新热度
        await hot_rank_service.increment_interaction(
            redis=redis,
            post_id=post_id,
            interaction_type='view',
            created_at=post.created_at
        )

        # 构建基础帖子数据
        post_dict = self._build_post_dict(post)

        # 添加投票数据
        upvotes, downvotes, score = await vote_service.get_vote_counts(redis, 'post', post.id)
        post_dict["upvotes"] = upvotes
        post_dict["downvotes"] = downvotes
        post_dict["score"] = score

        # 添加用户状态字段
        post_dict.update(await self._get_user_state(redis, post.id, current_user))

        # 添加评论数量
        post_dict["comment_count"] = await Comment.filter(post_id=post.id).count()

        return post_dict

    async def get_posts_list(
        self,
        redis: Redis,
        order_by: str = "-created_at",
        community_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        current_user: Optional[User] = None
    ) -> dict:
        """
        获取帖子列表（分页）

        Args:
            redis: Redis 客户端
            order_by: 排序字段
            community_id: 社区 ID 过滤
            skip: 跳过条数
            limit: 返回条数
            include_deleted: 是否包含已删除帖子
            current_user: 当前用户

        Returns:
            dict: 分页帖子列表
        """
        # 构建查询
        query = models.Post.all().order_by(order_by)
        query = query.select_related('author', 'community').prefetch_related('attachments')

        # 过滤软删除的帖子
        if not include_deleted:
            query = query.filter(deleted_at__isnull=True)

        if community_id:
            query = query.filter(community_id=community_id)

        # 获取总条数
        total = await query.count()

        # 获取当前页数据
        items_orm = await query.offset(skip).limit(limit)

        # 为每个帖子添加用户状态
        items = []
        if redis:
            # 即使没有登录用户，也需要从 Redis 获取投票数
            items = await self._enrich_posts_with_user_state(redis, items_orm, current_user)
        else:
            # 没有 Redis 时使用数据库字段（fallback）
            for post in items_orm:
                post_dict = schemas.PostOut.model_validate(post).model_dump()
                # 添加评论数量
                post_dict["comment_count"] = await Comment.filter(post_id=post.id).count()
                items.append(post_dict)

        # 计算是否有更多数据
        has_more = skip + limit < total

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more
        }

    async def get_my_posts(
        self,
        redis: Redis,
        user: User,
        skip: int = 0,
        limit: int = 20,
        is_highlighted: Optional[bool] = None
    ) -> dict:
        """
        获取当前用户的帖子列表（分页）

        Args:
            redis: Redis 客户端
            user: 当前用户
            skip: 跳过条数
            limit: 返回条数
            is_highlighted: 是否只返回精华帖子（None=全部）

        Returns:
            dict: 分页帖子列表
        """
        # 构建基础查询：只获取当前用户的未删除帖子
        query = models.Post.filter(
            author_id=user.id,
            deleted_at__isnull=True
        ).order_by("-created_at")

        # 添加精华筛选
        if is_highlighted is not None:
            query = query.filter(is_highlighted=is_highlighted)

        # 预加载关联
        query = query.select_related('author', 'community').prefetch_related('attachments')

        # 获取总数和分页数据
        total = await query.count()
        items_orm = await query.offset(skip).limit(limit)

        # 批量添加用户状态
        items = await self._enrich_posts_with_user_state(redis, items_orm, user)

        # 计算是否有更多数据
        has_more = skip + limit < total

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more
        }

    async def get_hot_posts(
        self,
        redis: Redis,
        community_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
        current_user: Optional[User] = None
    ) -> dict:
        """
        获取热门帖子列表

        Args:
            redis: Redis 客户端
            community_id: 社区 ID 过滤
            skip: 跳过条数
            limit: 返回条数
            current_user: 当前用户

        Returns:
            dict: 分页热门帖子列表
        """
        # 1. 从 Redis ZSET 获取热门 post_ids
        post_ids = await hot_rank_service.get_hot_post_ids(
            redis=redis,
            limit=limit,
            offset=skip,
            community_id=community_id
        )

        if not post_ids:
            return {
                "items": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "has_more": False
            }

        # 2. 批量获取缓存详情
        cached_posts = await post_cache_service.get_cached_posts_batch(redis, post_ids)

        # 3. 找出缓存未命中的帖子
        missing_ids = [pid for pid in post_ids if pid not in cached_posts]

        # 4. 从数据库获取未缓存的帖子
        if missing_ids:
            db_posts = await models.Post.filter(
                id__in=missing_ids,
                deleted_at__isnull=True
            ).select_related('author', 'community').prefetch_related('attachments')

            # 转换为字典并回填缓存
            for post in db_posts:
                post_dict = self._build_post_dict(post)

                # 从 Redis 获取最新投票数
                upvotes, downvotes, score = await vote_service.get_vote_counts(redis, 'post', post.id)
                post_dict["upvotes"] = upvotes
                post_dict["downvotes"] = downvotes
                post_dict["score"] = score

                # 添加评论数量
                post_dict["comment_count"] = await Comment.filter(post_id=post.id).count()

                cached_posts[post.id] = post_dict
                await post_cache_service.cache_post(redis, post.id, post_dict)

        # 5. 按 post_ids 顺序排序（保持热度顺序）
        items = []
        for pid in post_ids:
            if pid in cached_posts:
                post_dict = cached_posts[pid]
                # 确保评论数量存在（从缓存获取的可能没有）
                if "comment_count" not in post_dict:
                    post_dict["comment_count"] = await Comment.filter(post_id=pid).count()
                items.append(post_dict)

        # 6. 计算总数和是否有更多数据
        total = await redis.zcard(
            hot_rank_service._get_hot_posts_key(community_id)
        )
        has_more = skip + limit < total

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more
        }

    async def create_post(
        self,
        user: User,
        title: str,
        content: str,
        community_id: int,
        attachment_ids: Optional[List[int]] = None
    ) -> dict:
        """
        创建帖子

        Args:
            user: 当前用户
            title: 标题
            content: 内容
            community_id: 社区 ID
            attachment_ids: 附件 ID 列表

        Returns:
            dict: 创建的帖子

        Raises:
            Returns {"error": "..."} on failure
        """
        # 校验板块是否存在
        if not await Community.exists(id=community_id):
            return {"error": "社区不存在"}

        # 创建帖子（排除 attachment_ids，后面单独处理）
        post = await models.Post.create(
            title=title,
            content=content,
            community_id=community_id,
            author=user
        )

        # 更新社区帖子计数
        await Community.filter(id=community_id).update(
            post_count=F('post_count') + 1
        )

        # 关联附件
        if attachment_ids:
            # 验证附件是否存在且属于当前用户且未被使用
            attachments = await PostAttachment.filter(
                id__in=attachment_ids,
                uploader=user,
                post=None
            )

            if len(attachments) != len(attachment_ids):
                return {"error": "部分附件无效或已被使用"}

            # 批量更新附件的 post 关联
            await PostAttachment.filter(id__in=attachment_ids).update(
                post_id=post.id
            )

        # 重新获取帖子以预加载关联对象
        post = await models.Post.get(
            id=post.id
        ).select_related('author', 'community').prefetch_related('attachments')

        return self._build_post_dict(post)

    async def update_post(
        self,
        redis: Redis,
        post_id: int,
        user: User,
        title: Optional[str] = None,
        content: Optional[str] = None,
        attachment_ids: Optional[List[int]] = None
    ) -> dict:
        """
        更新帖子

        Args:
            redis: Redis 客户端
            post_id: 帖子 ID
            user: 当前用户
            title: 新标题
            content: 新内容
            attachment_ids: 附件 ID 列表

        Returns:
            dict: 更新的帖子

        Raises:
            Returns {"error": "..."} on failure
        """
        post = await models.Post.get_or_none(id=post_id)

        if not post:
            return {"error": "帖子不存在"}

        # 权限检查
        if post.author_id != user.id:
            return {"error": "无权编辑此帖子"}

        if post.deleted_at:
            return {"error": "无法编辑已删除的帖子"}

        # 更新字段
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content

        if update_data or attachment_ids is not None:
            await models.Post.filter(id=post_id).update(
                **update_data,
                is_edited=True
            )

            # 处理附件更新
            if attachment_ids is not None:
                result = await self._update_post_attachments(
                    post_id, attachment_ids, user
                )
                if "error" in result:
                    return result

            # 失效缓存
            await post_cache_service.invalidate_post(redis, post_id)

            # 重新获取帖子
            post = await models.Post.get(
                id=post_id
            ).select_related('author', 'community').prefetch_related('attachments')

        return self._build_post_dict(post)

    async def delete_post(
        self,
        post_id: int,
        user: User,
        reason: Optional[str] = None
    ) -> dict:
        """
        删除帖子

        Args:
            post_id: 帖子 ID
            user: 当前用户
            reason: 删除原因

        Returns:
            dict: 删除结果

        Raises:
            Returns {"error": "..."} on failure
        """
        post = await models.Post.get_or_none(id=post_id)

        if not post:
            return {"error": "帖子不存在"}

        if post.deleted_at:
            return {"error": "帖子已被删除"}

        # 权限检查
        from core.permissions import can_moderate_post

        is_author = post.author_id == user.id
        is_superuser = user.is_superuser
        is_moderator = False

        if not is_author and not is_superuser:
            _, membership = await can_moderate_post(post_id, user)
            is_moderator = membership is not None

        if not is_author and not is_moderator and not is_superuser:
            return {"error": "无权删除此帖子"}

        # 获取所有附件，用于删除 RustFS 文件
        attachments = await PostAttachment.filter(post_id=post_id)

        # 使用事务确保删除和审计日志的原子性
        async with transactions.in_transaction():
            await models.Post.filter(id=post_id).update(
                deleted_at=datetime.now(timezone.utc),
                deleted_by_id=user.id
            )

            # 更新社区帖子计数（减少）
            await Community.filter(id=post.community_id).update(
                post_count=F('post_count') - 1
            )

            await create_audit_log(
                actor=user,
                target_type=TargetType.POST,
                target_id=post_id,
                action_type=ActionType.DELETE_POST,
                reason=reason,
                metadata={"is_author": is_author, "is_moderator": is_moderator}
            )

        # 删除 RustFS 中的文件
        for attachment in attachments:
            await rustfs_service.delete_file(attachment.file_url)

        # 从 Redis 热门榜中移除
        redis_dep = get_redis()
        redis_client = await redis_dep.__anext__()
        try:
            await hot_rank_service.remove_post(
                redis=redis_client,
                post_id=post_id,
                community_id=post.community_id
            )
            await post_cache_service.invalidate_post(redis_client, post_id)
        finally:
            await redis_client.close()

        return {"message": "帖子删除成功"}

    async def restore_post(
        self,
        post_id: int,
        user: User,
        reason: Optional[str] = None
    ) -> dict:
        """
        恢复帖子

        Args:
            post_id: 帖子 ID
            user: 当前用户
            reason: 恢复原因

        Returns:
            dict: 恢复结果

        Raises:
            Returns {"error": "..."} on failure
        """
        post = await models.Post.get_or_none(id=post_id)

        if not post:
            return {"error": "帖子不存在"}

        if not post.deleted_at:
            return {"error": "帖子未被删除"}

        # 使用事务确保恢复和审计日志的原子性
        async with transactions.in_transaction():
            await models.Post.filter(id=post_id).update(
                deleted_at=None,
                deleted_by_id=None
            )

            await create_audit_log(
                actor=user,
                target_type=TargetType.POST,
                target_id=post_id,
                action_type=ActionType.RESTORE_POST,
                reason=reason
            )

        return {"message": "帖子恢复成功"}

    async def lock_post(
        self,
        post_id: int,
        is_locked: bool,
        user: User,
        reason: Optional[str] = None
    ) -> dict:
        """锁定/解锁帖子"""
        return await self._update_moderation(
            post_id=post_id,
            field_name="is_locked",
            value=is_locked,
            action_true=ActionType.LOCK_POST,
            action_false=ActionType.UNLOCK_POST,
            success_message_true="帖子已锁定",
            success_message_false="帖子已解锁",
            permission_error="仅版主可以锁定帖子",
            user=user,
            reason=reason
        )

    async def highlight_post(
        self,
        post_id: int,
        is_highlighted: bool,
        user: User,
        reason: Optional[str] = None
    ) -> dict:
        """设为/取消精华"""
        return await self._update_moderation(
            post_id=post_id,
            field_name="is_highlighted",
            value=is_highlighted,
            action_true=ActionType.HIGHLIGHT_POST,
            action_false=ActionType.UNHIGHLIGHT_POST,
            success_message_true="已设置精华",
            success_message_false="已取消精华",
            permission_error="仅版主可以设置精华",
            user=user,
            reason=reason
        )

    async def pin_post(
        self,
        post_id: int,
        is_pinned: bool,
        user: User,
        reason: Optional[str] = None
    ) -> dict:
        """置顶/取消置顶"""
        return await self._update_moderation(
            post_id=post_id,
            field_name="is_pinned",
            value=is_pinned,
            action_true=ActionType.PIN_POST,
            action_false=ActionType.UNPIN_POST,
            success_message_true="帖子已置顶",
            success_message_false="帖子已取消置顶",
            permission_error="仅版主可以置顶帖子",
            user=user,
            reason=reason
        )

    # --- 辅助方法 ---

    def _build_post_dict(self, post: models.Post) -> dict:
        """构建帖子字典"""
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "score": post.score,
            "hot_rank": post.hot_rank,
            "author_id": post.author_id,
            "community_id": post.community_id,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "avatar": post.author.avatar,  # 包含作者头像
            } if post.author else None,
            "community": {
                "id": post.community.id,
                "name": post.community.name,
            } if post.community else None,
            "attachments": [
                {
                    "id": a.id,
                    "attachment_type": a.attachment_type.value if hasattr(a.attachment_type, 'value') else str(a.attachment_type),
                    "file_name": a.file_name,
                    "file_url": a.file_url,
                    "file_size": a.file_size,
                    "mime_type": a.mime_type,
                    "sort_order": a.sort_order,
                }
                for a in post.attachments
            ],
            "is_edited": post.is_edited,
            "is_locked": post.is_locked,
            "is_highlighted": post.is_highlighted,
            "is_pinned": post.is_pinned,
            "deleted_by_id": post.deleted_by_id,
            "deleted_at": post.deleted_at,  # 保持 datetime 对象
            "created_at": post.created_at,  # 保持 datetime 对象
            "updated_at": post.updated_at,  # 保持 datetime 对象或 None
            "upvotes": post.upvotes,
            "downvotes": post.downvotes,
            "user_vote": 0,
            "bookmarked": False,
            "bookmark_count": 0,
            "comment_count": 0,
        }

    async def _get_user_state(
        self,
        redis: Redis,
        post_id: int,
        current_user: Optional[User]
    ) -> dict:
        """获取用户状态字段"""
        if current_user:
            user_vote = await vote_service.get_user_vote_status(
                redis, current_user.id, 'post', post_id
            )
            bookmarked = await bookmark_service.is_bookmarked(
                redis, current_user.id, post_id
            )
        else:
            user_vote = 0
            bookmarked = False

        bookmark_count = await bookmark_service.get_bookmark_count(
            redis, post_id
        )

        return {
            "user_vote": user_vote,
            "bookmarked": bookmarked,
            "bookmark_count": bookmark_count
        }

    async def _enrich_posts_with_user_state(
        self,
        redis: Redis,
        posts: List[models.Post],
        current_user: Optional[User] = None
    ) -> List[dict]:
        """为帖子列表批量添加用户状态"""
        post_ids = [p.id for p in posts]

        # 批量获取投票状态（仅当用户已登录时）
        if current_user:
            vote_statuses = await vote_service.batch_get_vote_statuses(
                redis, current_user.id, [('post', pid) for pid in post_ids]
            )
            # 批量获取收藏状态
            bookmark_statuses = await bookmark_service.batch_check_bookmarked(
                redis, current_user.id, post_ids
            )
        else:
            vote_statuses = {}
            bookmark_statuses = {}

        # 批量获取收藏数（所有用户都能看到）
        bookmark_counts = await bookmark_service.batch_get_bookmark_counts(
            redis, post_ids
        )

        # 构建响应数据
        items = []
        for post in posts:
            post_dict = self._build_post_dict(post)

            # 从 Redis 获取最新投票数
            upvotes, downvotes, score = await vote_service.get_vote_counts(redis, 'post', post.id)
            post_dict["upvotes"] = upvotes
            post_dict["downvotes"] = downvotes
            post_dict["score"] = score

            # 添加用户状态字段
            post_dict["user_vote"] = vote_statuses.get(('post', post.id), 0) if current_user else 0
            post_dict["bookmarked"] = bookmark_statuses.get(post.id, False) if current_user else False
            post_dict["bookmark_count"] = bookmark_counts.get(post.id, 0)

            # 添加评论数量
            post_dict["comment_count"] = await Comment.filter(post_id=post.id).count()

            items.append(post_dict)

        return items

    async def _update_post_attachments(
        self,
        post_id: int,
        attachment_ids: List[int],
        user: User
    ) -> dict:
        """更新帖子附件"""
        # 获取当前附件
        current_attachments = await PostAttachment.filter(post_id=post_id)
        current_ids = {a.id for a in current_attachments}
        new_ids = set(attachment_ids)

        # 找出需要移除的附件
        to_remove = current_ids - new_ids
        # 找出需要添加的附件
        to_add = new_ids - current_ids

        # 移除不再使用的附件
        if to_remove:
            for attachment in await PostAttachment.filter(id__in=to_remove):
                await rustfs_service.delete_file(attachment.file_url)
            await PostAttachment.filter(id__in=to_remove).delete()

        # 添加新附件
        if to_add:
            attachments = await PostAttachment.filter(
                id__in=to_add,
                uploader=user,
                post=None
            )

            if len(attachments) != len(to_add):
                return {"error": "部分附件无效或已被使用"}

            await PostAttachment.filter(id__in=to_add).update(post_id=post_id)

        return {}

    async def _update_moderation(
        self,
        post_id: int,
        field_name: str,
        value: bool,
        action_true: ActionType,
        action_false: ActionType,
        success_message_true: str,
        success_message_false: str,
        permission_error: str,
        user: User,
        reason: Optional[str] = None
    ) -> dict:
        """通用的帖子管理更新"""
        from core.permissions import can_moderate_post

        post, membership = await can_moderate_post(post_id, user)

        if not membership:
            return {"error": permission_error}

        action = action_true if value else action_false

        async with transactions.in_transaction():
            await models.Post.filter(id=post_id).update(**{field_name: value})

            await create_audit_log(
                actor=user,
                target_type=TargetType.POST,
                target_id=post_id,
                action_type=action,
                reason=reason
            )

        return {"message": success_message_true if value else success_message_false}


# 导出服务实例
post_service = PostService()

__all__ = ["PostService", "post_service"]
