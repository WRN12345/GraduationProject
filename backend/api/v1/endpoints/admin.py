"""
@Created on : 2026/4/3
@Author: wrn
@Des: 超级管理员 API 端点 - 所有端点需要管理员权限
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Optional
from models.user import User
from core.security import get_current_admin
from schemas import admin as schemas
from core.services.admin.admin_service import admin_service
from core.services.admin.audit_service import audit_service


from core.services.admin.content_management_service import AdminErrorCode, ERROR_STATUS_MAP

router = APIRouter(
    tags=["超级管理员"],
    dependencies=[Depends(get_current_admin)]
)


# ==================== 控制面板 ====================

@router.get("/admin/dashboard", response_model=schemas.DashboardStats, summary="获取控制面板统计数据")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin)
):
    """获取控制面板统计数据（仅超级管理员）"""
    return await admin_service.get_dashboard_stats()


# ==================== 用户管理 ====================

@router.get("/admin/users", response_model=schemas.PaginatedAdminUserResponse, summary="获取所有用户列表")
async def get_all_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="筛选激活状态"),
    is_superuser: Optional[bool] = Query(None, description="筛选管理员"),
    search: Optional[str] = Query(None, max_length=100, description="搜索用户名/昵称"),
    current_user: User = Depends(get_current_admin)
):
    """获取所有用户列表（支持筛选和搜索，仅超级管理员）"""
    return await admin_service.get_all_users(
        page=page,
        page_size=page_size,
        is_active=is_active,
        is_superuser=is_superuser,
        search=search
    )


@router.get("/admin/users/{user_id}", response_model=schemas.AdminUserDetailOut, summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_admin)
):
    """获取用户详细信息（管理员视角，仅超级管理员）"""
    result = await admin_service.get_user_detail(user_id)

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_404_NOT_FOUND),
            detail=result["error"]
        )

    return result


@router.post("/admin/users/{user_id}/ban", response_model=schemas.AdminActionResponse, summary="冻结用户")
async def ban_user(
    user_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """冻结用户（设置 is_active=False，仅超级管理员）"""
    result = await admin_service.ban_user(
        user_id=user_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


@router.post("/admin/users/{user_id}/unban", response_model=schemas.AdminActionResponse, summary="解冻用户")
async def unban_user(
    user_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """解冻用户（设置 is_active=True，仅超级管理员）"""
    result = await admin_service.unban_user(
        user_id=user_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


# ==================== 帖子管理 ====================

@router.get("/admin/posts", response_model=schemas.PaginatedAdminPostResponse, summary="获取所有帖子列表")
async def get_all_posts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    include_deleted: bool = Query(False, description="是否包含已删除帖子"),
    search: Optional[str] = Query(None, max_length=100, description="搜索标题/内容"),
    current_user: User = Depends(get_current_admin)
):
    """获取所有帖子列表（管理员视角，支持包含已删除帖子，支持中文搜索）"""
    return await admin_service.get_all_posts(
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
        search=search
    )


@router.get("/admin/posts/{post_id}", response_model=schemas.AdminPostDetailOut, summary="获取帖子详情")
async def get_post_detail(
    post_id: int,
    current_user: User = Depends(get_current_admin)
):
    """获取帖子详情（管理员视角，可查看已删除帖子）"""
    result = await admin_service.get_post_detail(post_id)

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_404_NOT_FOUND),
            detail=result["error"]
        )

    return result


@router.delete("/admin/posts/{post_id}", response_model=schemas.AdminActionResponse, summary="管理员软删除帖子")
async def admin_delete_post(
    post_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """管理员软删除帖子（仅超级管理员）"""
    result = await admin_service.delete_post(
        post_id=post_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


@router.post("/admin/posts/{post_id}/restore", response_model=schemas.AdminActionResponse, summary="管理员恢复帖子")
async def admin_restore_post(
    post_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """管理员恢复已软删除的帖子（仅超级管理员）"""
    result = await admin_service.restore_post(
        post_id=post_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


@router.delete("/admin/posts/{post_id}/hard", response_model=schemas.AdminActionResponse, summary="管理员硬删除帖子")
async def admin_hard_delete_post(
    post_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """管理员硬删除帖子（永久删除，不可逆，仅超级管理员）"""
    result = await admin_service.hard_delete_post(
        post_id=post_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


# ==================== 评论管理 ====================

@router.get("/admin/comments", response_model=schemas.PaginatedAdminCommentResponse, summary="获取所有评论列表")
async def get_all_comments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    include_deleted: bool = Query(False, description="是否包含已删除评论"),
    search: Optional[str] = Query(None, max_length=100, description="搜索评论内容"),
    current_user: User = Depends(get_current_admin)
):
    """获取所有评论列表（管理员视角，支持包含已删除评论，支持中文搜索）"""
    return await admin_service.get_all_comments(
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
        search=search
    )


@router.delete("/admin/comments/{comment_id}", response_model=schemas.AdminActionResponse, summary="管理员软删除评论")
async def admin_delete_comment(
    comment_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """管理员软删除评论（仅超级管理员）"""
    result = await admin_service.delete_comment(
        comment_id=comment_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


@router.post("/admin/comments/{comment_id}/restore", response_model=schemas.AdminActionResponse, summary="管理员恢复评论")
async def admin_restore_comment(
    comment_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """管理员恢复已软删除的评论（仅超级管理员）"""
    result = await admin_service.restore_comment(
        comment_id=comment_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


@router.delete("/admin/comments/{comment_id}/hard", response_model=schemas.AdminActionResponse, summary="管理员硬删除评论")
async def admin_hard_delete_comment(
    comment_id: int,
    body: schemas.UserActionRequest = Body(default=schemas.UserActionRequest()),
    current_user: User = Depends(get_current_admin)
):
    """管理员硬删除评论（永久删除，不可逆，仅超级管理员）"""
    result = await admin_service.hard_delete_comment(
        comment_id=comment_id,
        admin_user=current_user,
        reason=body.reason
    )

    if "error" in result:
        raise HTTPException(
            status_code=ERROR_STATUS_MAP.get(result["code"], status.HTTP_400_BAD_REQUEST),
            detail=result["error"]
        )

    return result


# ==================== 审计日志 ====================

@router.get("/admin/audit-logs", response_model=schemas.PaginatedAdminAuditLogResponse, summary="获取审计日志列表")
async def get_audit_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    admin_id: Optional[int] = Query(None, description="筛选指定管理员的日志"),
    action_type: Optional[int] = Query(None, description="筛选操作类型"),
    target_type: Optional[int] = Query(None, description="筛选目标类型"),
    current_user: User = Depends(get_current_admin)
):
    """获取审计日志列表（支持多维度筛选，仅超级管理员）"""
    if admin_id is not None:
        return await admin_service.get_admin_audit_logs(
            admin_id=admin_id,
            page=page,
            page_size=page_size,
            action_type=action_type,
            target_type=target_type
        )
    else:
        return await admin_service.get_all_audit_logs(
            page=page,
            page_size=page_size,
            action_type=action_type,
            target_type=target_type
        )


# ==================== 图表数据 ====================

@router.get("/admin/stats/action-stats", response_model=schemas.ActionStatsResponse, summary="操作类型统计")
async def get_action_stats(
    current_user: User = Depends(get_current_admin)
):
    """按操作类型聚合统计（用于图表，仅超级管理员）"""
    return await audit_service.get_action_stats()


@router.get("/admin/stats/trend", response_model=schemas.TrendResponse, summary="操作趋势")
async def get_trend(
    days: int = Query(30, ge=7, le=90, description="统计天数"),
    current_user: User = Depends(get_current_admin)
):
    """获取最近 N 天的操作趋势（用于图表，仅超级管理员）"""
    return await audit_service.get_trend(days=days)
