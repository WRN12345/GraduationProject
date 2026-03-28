"""
@Created on : 2026/3/15
@Author: wrn
@Des: 用户服务 - 用户管理 + 头像上传 + Karma 计算
"""
from typing import Optional, Dict, Any
from models.user import User
from models.post import Post
from models.comment import Comment
from models.vote import Vote
from core.security import get_password_hash, verify_password
from core.services.infrastructure.rustfs_service import rustfs_service
import logging

logger = logging.getLogger(__name__)


class UserService:
    """用户服务 - 用户管理 + 头像上传"""

    async def get_user_info(
        self,
        user: User
    ) -> dict:
        """
        获取当前用户信息

        Args:
            user: 当前用户

        Returns:
            dict: 用户信息
        """
        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "bio": user.bio,
            "avatar": user.avatar,
            "karma": user.karma,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "last_login": user.last_login
        }

    async def update_user_info(
        self,
        user: User,
        **update_data
    ) -> dict:
        """
        更新用户信息

        Args:
            user: 当前用户
            **update_data: 更新数据

        Returns:
            dict: 更新后的用户信息
        """
        # 不允许修改用户名
        if "username" in update_data:
            del update_data["username"]

        if update_data:
            await User.filter(id=user.id).update(**update_data)
            await user.refresh_from_db()

        return await self.get_user_info(user)

    async def update_username(
        self,
        user: User,
        new_username: str
    ) -> dict:
        """
        修改用户名

        Args:
            user: 当前用户
            new_username: 新用户名

        Returns:
            dict: 更新后的用户信息

        Raises:
            Returns {"error": "..."} on failure
        """
        # 检查是否与当前用户名相同
        if new_username == user.username:
            return {"error": "新用户名不能与当前用户名相同"}

        # 检查用户名是否已存在
        existing_user = await User.get_or_none(username=new_username)
        if existing_user:
            return {"error": "该用户名已被占用"}

        # 更新用户名
        await User.filter(id=user.id).update(username=new_username)
        await user.refresh_from_db()

        return await self.get_user_info(user)

    async def update_password(
        self,
        user: User,
        old_password: str,
        new_password: str
    ) -> dict:
        """
        修改密码

        Args:
            user: 当前用户
            old_password: 旧密码
            new_password: 新密码

        Returns:
            dict: 更新结果

        Raises:
            Returns {"error": "..."} on failure
        """
        # 验证旧密码
        if not verify_password(old_password, user.password):
            return {"error": "旧密码错误"}

        # 检查新密码是否与旧密码相同
        if old_password == new_password:
            return {"error": "新密码不能与旧密码相同"}

        # 更新密码
        hashed_password = get_password_hash(new_password)
        await User.filter(id=user.id).update(password=hashed_password)

        return {"message": "密码修改成功"}

    async def update_user_profile(
        self,
        user: User,
        **update_data
    ) -> dict:
        """
        更新用户资料

        Args:
            user: 当前用户
            **update_data: 更新数据

        Returns:
            dict: 更新后的用户信息
        """
        if update_data:
            await User.filter(id=user.id).update(**update_data)
            await user.refresh_from_db()

        return await self.get_user_info(user)

    async def upload_avatar(
        self,
        user: User,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> dict:
        """
        上传用户头像

        Args:
            user: 当前用户
            file_data: 文件数据
            filename: 文件名
            content_type: 内容类型

        Returns:
            dict: 上传结果

        Raises:
            Returns {"error": "..."} on failure
        """
        # 验证文件类型
        if not content_type or not content_type.startswith('image/'):
            return {"error": "只能上传图片文件"}

        # 文件大小限制
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        if len(file_data) > MAX_SIZE:
            return {"error": "头像大小不能超过 5MB"}

        # 上传到 RustFS
        url = await rustfs_service.upload_file(
            file_data=file_data,
            filename=f"avatar_{user.id}_{filename}",
            content_type=content_type
        )

        # 更新用户头像
        await User.filter(id=user.id).update(avatar=url)
        await user.refresh_from_db()

        return {
            "avatar_url": url,
            "message": "头像上传成功"
        }

    async def get_user_profile(
        self,
        username: str
    ) -> dict:
        """
        获取公开用户资料

        Args:
            username: 用户名

        Returns:
            dict: 用户资料

        Raises:
            Returns {"error": "..."} on failure
        """
        user = await User.get_or_none(username=username)
        if not user:
            return {"error": "用户不存在"}

        # 计算统计数据
        post_count = await Post.filter(author=user, deleted_at__isnull=True).count()
        comment_count = await Comment.filter(author=user, deleted_at__isnull=True).count()

        # 计算点赞和点踩数量
        from models.vote import Vote
        upvote_count = await Vote.filter(user=user, direction=1).count()
        downvote_count = await Vote.filter(user=user, direction=-1).count()

        # 如果 karma 为 0，触发计算
        if user.karma == 0:
            await user.calculate_karma()
            await user.refresh_from_db()

        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "bio": user.bio,
            "avatar": user.avatar,
            "karma": user.karma,
            "created_at": user.created_at,
            "is_active": user.is_active,
            "post_count": post_count,
            "comment_count": comment_count,
            "upvote_count": upvote_count,
            "downvote_count": downvote_count,
        }

    async def get_user_posts(
        self,
        username: str,
        skip: int = 0,
        limit: int = 20
    ) -> list:
        """
        获取用户发布的帖子

        Args:
            username: 用户名
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 用户帖子列表

        Raises:
            Returns {"error": "..."} on failure
        """
        user = await User.get_or_none(username=username)
        if not user:
            return {"error": "用户不存在"}

        posts = await Post.filter(
            author=user,
            deleted_at__isnull=True
        ).order_by("-created_at").offset(skip).limit(limit).prefetch_related('author', 'community')

        # 手动序列化，确保包含关联对象
        result = []
        for post in posts:
            result.append({
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
                    "avatar": post.author.avatar
                } if post.author else None,
                "community": {
                    "id": post.community.id,
                    "name": post.community.name
                } if post.community else None,
                "upvotes": post.upvotes,
                "downvotes": post.downvotes,
                "comment_count": getattr(post, 'comment_count', 0),
                "user_vote": 0,
                "bookmarked": False,
                "bookmark_count": 0,
                "is_edited": post.is_edited,
                "is_locked": post.is_locked,
                "is_highlighted": post.is_highlighted,
                "is_pinned": post.is_pinned,
                "deleted_at": post.deleted_at,
                "created_at": post.created_at,
                "updated_at": post.updated_at
            })

        return result

    async def get_user_comments(
        self,
        username: str,
        skip: int = 0,
        limit: int = 50
    ) -> dict:
        """
        获取用户发表的评论

        Args:
            username: 用户名
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 用户评论列表

        Raises:
            Returns {"error": "..."} on failure
        """
        user = await User.get_or_none(username=username)
        if not user:
            return {"error": "用户不存在"}

        comments = await Comment.filter(
            author=user,
            deleted_at__isnull=True
        ).order_by("-created_at").offset(skip).limit(limit).prefetch_related('author', 'post')

        # 手动序列化，确保包含关联对象
        result = []
        for comment in comments:
            # 安全地访问 post 关系
            post_data = None
            if comment.post:
                post_data = {
                    "id": comment.post.id,
                    "title": comment.post.title
                }

            result.append({
                "id": comment.id,
                "content": comment.content,
                "author_id": comment.author_id,
                "author": {
                    "id": comment.author.id,
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                    "nickname": comment.author.nickname
                } if comment.author else None,
                "post_id": comment.post_id,
                "post": post_data,
                "parent_id": comment.parent_id,
                "upvotes": comment.upvotes,
                "downvotes": comment.downvotes,
                "score": comment.score,
                "is_edited": comment.is_edited,
                "deleted_at": comment.deleted_at,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at
            })

        return result

    async def get_user_activity(
        self,
        username: str
    ) -> dict:
        """
        获取用户的活动汇总

        Args:
            username: 用户名

        Returns:
            dict: 用户活动数据

        Raises:
            Returns {"error": "..."} on failure
        """
        user = await User.get_or_none(username=username)
        if not user:
            return {"error": "用户不存在"}

        # 获取最近的帖子
        posts = await Post.filter(
            author=user,
            deleted_at__isnull=True
        ).order_by("-created_at").limit(10).values()

        # 获取最近的评论
        comments = await Comment.filter(
            author=user,
            deleted_at__isnull=True
        ).order_by("-created_at").limit(10).values()

        # 获取总数
        total_posts = await Post.filter(author=user).count()
        total_comments = await Comment.filter(author=user).count()

        return {
            "posts": list(posts),
            "comments": list(comments),
            "total_posts": total_posts,
            "total_comments": total_comments,
        }

    async def get_user_upvoted(
        self,
        username: str,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        获取用户点赞的内容（帖子和评论）

        Args:
            username: 用户名
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 用户点赞的内容列表

        Raises:
            Returns {"error": "..."} on failure
        """
        user = await User.get_or_none(username=username)
        if not user:
            return {"error": "用户不存在"}

        # 获取用户点赞的记录（direction = 1），按 id 降序排序
        votes = await Vote.filter(
            user=user,
            direction=1
        ).order_by("-id").offset(skip).limit(limit).prefetch_related('post', 'comment__post')

        # 整理结果
        result = []
        for vote in votes:
            if vote.post:
                result.append({
                    "id": vote.post.id,
                    "type": "post",
                    "post_id": vote.post.id,
                    "title": vote.post.title,
                    "content": vote.post.content,
                    "created_at": vote.post.created_at,
                    "upvotes": vote.post.upvotes,
                    "downvotes": vote.post.downvotes,
                })
            elif vote.comment:
                result.append({
                    "id": vote.comment.id,
                    "type": "comment",
                    "post_id": vote.comment.post_id,
                    "content": vote.comment.content,
                    "created_at": vote.comment.created_at,
                    "upvotes": vote.comment.upvotes,
                    "downvotes": vote.comment.downvotes,
                    "post": {
                        "id": vote.comment.post_id,
                        "title": vote.comment.post.title if vote.comment.post else "未知帖子"
                    } if vote.comment.post else None
                })

        return result

    async def get_user_downvoted(
        self,
        username: str,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        获取用户点踩的内容（帖子和评论）

        Args:
            username: 用户名
            skip: 跳过条数
            limit: 返回条数

        Returns:
            dict: 用户点踩的内容列表

        Raises:
            Returns {"error": "..."} on failure
        """
        user = await User.get_or_none(username=username)
        if not user:
            return {"error": "用户不存在"}

        # 获取用户点踩的记录（direction = -1），按 id 降序排序
        votes = await Vote.filter(
            user=user,
            direction=-1
        ).order_by("-id").offset(skip).limit(limit).prefetch_related('post', 'comment__post')

        # 整理结果
        result = []
        for vote in votes:
            if vote.post:
                result.append({
                    "id": vote.post.id,
                    "type": "post",
                    "post_id": vote.post.id,
                    "title": vote.post.title,
                    "content": vote.post.content,
                    "created_at": vote.post.created_at,
                    "upvotes": vote.post.upvotes,
                    "downvotes": vote.post.downvotes,
                })
            elif vote.comment:
                result.append({
                    "id": vote.comment.id,
                    "type": "comment",
                    "post_id": vote.comment.post_id,
                    "content": vote.comment.content,
                    "created_at": vote.comment.created_at,
                    "upvotes": vote.comment.upvotes,
                    "downvotes": vote.comment.downvotes,
                    "post": {
                        "id": vote.comment.post_id,
                        "title": vote.comment.post.title if vote.comment.post else "未知帖子"
                    } if vote.comment.post else None
                })

        return result


# 导出服务实例
user_service = UserService()

__all__ = ["UserService", "user_service"]
