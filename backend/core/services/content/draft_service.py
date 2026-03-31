"""
@Created on : 2026/3/31
@Author: wrn
@Des: 草稿服务 - 草稿 CRUD
"""
from typing import Optional, List
from models.user import User
from models.draft import Draft
from schemas import draft as schemas
import logging

logger = logging.getLogger(__name__)


class DraftService:
    """草稿服务"""

    async def create_draft(
        self,
        user: User,
        title: str = "",
        content: str = "",
        community_id: Optional[int] = None,
        attachment_ids: Optional[List[int]] = None
    ) -> dict:
        """
        创建草稿
        
        Args:
            user: 当前用户
            title: 标题
            content: 内容
            community_id: 社区ID
            attachment_ids: 附件ID列表
            
        Returns:
            dict: 草稿数据或错误信息
        """
        try:
            draft = await Draft.create(
                title=title,
                content=content,
                author=user,
                community_id=community_id,
                attachment_ids=attachment_ids or []
            )
            
            # 重新查询以获取关联数据
            draft = await Draft.get(id=draft.id).select_related('community')
            
            return self._build_draft_dict(draft)
        except Exception as e:
            logger.error(f"创建草稿失败: {e}")
            return {"error": f"创建草稿失败: {str(e)}"}

    async def update_draft(
        self,
        draft_id: int,
        user: User,
        title: Optional[str] = None,
        content: Optional[str] = None,
        community_id: Optional[int] = None,
        attachment_ids: Optional[List[int]] = None
    ) -> dict:
        """
        更新草稿
        
        Args:
            draft_id: 草稿ID
            user: 当前用户
            title: 标题
            content: 内容
            community_id: 社区ID
            attachment_ids: 附件ID列表
            
        Returns:
            dict: 草稿数据或错误信息
        """
        draft = await Draft.get_or_none(id=draft_id, author=user).select_related('community')
        
        if not draft:
            return {"error": "草稿不存在或无权操作"}
        
        # 更新非空字段
        if title is not None:
            draft.title = title
        if content is not None:
            draft.content = content
        if community_id is not None:
            draft.community_id = community_id
        if attachment_ids is not None:
            draft.attachment_ids = attachment_ids
            
        await draft.save()
        
        # 重新查询以获取关联数据
        draft = await Draft.get(id=draft.id).select_related('community')
        
        return self._build_draft_dict(draft)

    async def delete_draft(self, draft_id: int, user: User) -> dict:
        """
        删除草稿
        
        Args:
            draft_id: 草稿ID
            user: 当前用户
            
        Returns:
            dict: 操作结果
        """
        draft = await Draft.get_or_none(id=draft_id, author=user)
        
        if not draft:
            return {"error": "草稿不存在或无权操作"}
        
        await draft.delete()
        return {"message": "草稿已删除"}

    async def get_draft_detail(self, draft_id: int, user: User) -> dict:
        """
        获取草稿详情
        
        Args:
            draft_id: 草稿ID
            user: 当前用户
            
        Returns:
            dict: 草稿数据或错误信息
        """
        draft = await Draft.get_or_none(id=draft_id, author=user).select_related('community')
        
        if not draft:
            return {"error": "草稿不存在或无权操作"}
        
        return self._build_draft_dict(draft)

    async def get_user_drafts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """
        获取用户的草稿列表（分页）
        
        Args:
            user: 当前用户
            skip: 跳过数量
            limit: 每页数量
            
        Returns:
            dict: 分页草稿数据
        """
        # 查询总数
        total = await Draft.filter(author=user).count()
        
        # 查询草稿列表
        drafts = await Draft.filter(author=user).select_related('community').order_by('-updated_at').offset(skip).limit(limit)
        
        items = [self._build_draft_dict(d) for d in drafts]
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }

    async def get_draft_count(self, user: User) -> int:
        """获取用户草稿数量"""
        return await Draft.filter(author=user).count()

    def _build_draft_dict(self, draft: Draft) -> dict:
        """构建草稿字典"""
        result = {
            "id": draft.id,
            "title": draft.title,
            "content": draft.content,
            "author_id": draft.author_id,
            "community_id": draft.community_id,
            "attachment_ids": draft.attachment_ids or [],
            "created_at": draft.created_at,
            "updated_at": draft.updated_at,
        }
        
        if draft.community:
            result["community"] = {
                "id": draft.community.id,
                "name": draft.community.name,
            }
        else:
            result["community"] = None
            
        return result


# 单例
draft_service = DraftService()
