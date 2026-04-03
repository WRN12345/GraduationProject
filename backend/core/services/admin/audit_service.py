"""
@Created on : 2026/4/3
@Author: wrn
@Des: 管理员审计日志服务 - 审计日志查询与筛选
"""
from typing import Optional, List
from models.user import User
from models.audit_log import AuditLog, ActionType
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """管理员审计日志服务"""

    ADMIN_ACTION_TYPES = [
        ActionType.ADMIN_DELETE_POST.value,
        ActionType.ADMIN_RESTORE_POST.value,
        ActionType.ADMIN_HARD_DELETE_POST.value,
        ActionType.ADMIN_DELETE_COMMENT.value,
        ActionType.ADMIN_HARD_DELETE_COMMENT.value,
        ActionType.ADMIN_RESTORE_COMMENT.value,
        ActionType.BAN_USER.value,
        ActionType.UNBAN_USER.value,
    ]

    async def get_admin_audit_logs(
        self,
        admin_id: int,
        page: int = 1,
        page_size: int = 20,
        action_type: Optional[int] = None,
        target_type: Optional[int] = None
    ) -> dict:
        """
        获取指定管理员的操作日志

        Args:
            admin_id: 管理员用户 ID
            page: 页码
            page_size: 每页数量
            action_type: 操作类型筛选
            target_type: 目标类型筛选

        Returns:
            dict: 分页审计日志列表
        """
        query = AuditLog.filter(
            actor_id=admin_id,
            action_type__in=self.ADMIN_ACTION_TYPES
        ).order_by("-created_at")

        # 可选筛选条件
        if action_type is not None:
            query = query.filter(action_type=action_type)
        if target_type is not None:
            query = query.filter(target_type=target_type)

        total = await query.count()
        skip = (page - 1) * page_size
        logs = await query.offset(skip).limit(page_size)

        items = await self._serialize_logs(logs)
        has_more = skip + page_size < total

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": has_more,
        }

    async def get_all_audit_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        action_type: Optional[int] = None,
        target_type: Optional[int] = None,
        actor_id: Optional[int] = None
    ) -> dict:
        """
        获取所有审计日志（支持多维度筛选）

        Args:
            page: 页码
            page_size: 每页数量
            action_type: 操作类型筛选
            target_type: 目标类型筛选
            actor_id: 操作者 ID 筛选

        Returns:
            dict: 分页审计日志列表
        """
        query = AuditLog.all().order_by("-created_at")

        # 可选筛选条件
        if action_type is not None:
            query = query.filter(action_type=action_type)
        if target_type is not None:
            query = query.filter(target_type=target_type)
        if actor_id is not None:
            query = query.filter(actor_id=actor_id)

        total = await query.count()
        skip = (page - 1) * page_size
        logs = await query.offset(skip).limit(page_size)

        items = await self._serialize_logs(logs)
        has_more = skip + page_size < total

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": has_more,
        }

    async def _serialize_logs(self, logs: List[AuditLog]) -> List[dict]:
        """
        序列化审计日志列表，批量获取操作者用户名

        Args:
            logs: AuditLog 对象列表

        Returns:
            List[dict]: 序列化后的日志列表
        """
        items = []
        for log in logs:
            items.append({
                "id": log.id,
                "actor_id": log.actor_id,
                "actor_name": None,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "action_type": log.action_type,
                "reason": log.reason,
                "metadata": log.metadata,
                "created_at": log.created_at,
            })

        # 批量获取操作者用户名（避免 N+1 查询）
        if items:
            actor_ids = {item["actor_id"] for item in items}
            actors = await User.filter(id__in=actor_ids).values("id", "username")
            actor_map = {a["id"]: a["username"] for a in actors}
            for item in items:
                item["actor_name"] = actor_map.get(item["actor_id"])

        return items


# 导出服务实例
audit_service = AuditService()

__all__ = ["AuditService", "audit_service"]
