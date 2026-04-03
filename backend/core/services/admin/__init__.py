"""
超级管理员服务模块

采用门面模式（Facade Pattern）:
- admin_service: 统一入口门面，委托给子服务
- stats_service: 数据统计 + 用户管理
- content_management_service: 帖子/评论管理
- audit_service: 审计日志查询
"""
from .admin_service import admin_service, AdminService
from .stats_service import stats_service, StatsService
from .content_management_service import content_management_service, ContentManagementService
from .audit_service import audit_service, AuditService

__all__ = [
    "admin_service",
    "AdminService",
    "stats_service",
    "StatsService",
    "content_management_service",
    "ContentManagementService",
    "audit_service",
    "AuditService",
]
