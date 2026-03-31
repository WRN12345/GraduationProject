"""
@Created on : 2026/3/31
@Author: wrn
@Des: 草稿管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from models.user import User
from core.security import get_current_user
from core.services import draft_service
from schemas import draft as draft_schemas

router = APIRouter(tags=["草稿管理"])


@router.post("/drafts", response_model=draft_schemas.DraftOut, summary="创建草稿")
async def create_draft(
    draft_in: draft_schemas.DraftCreate,
    current_user: User = Depends(get_current_user),
):
    """创建新草稿"""
    result = await draft_service.create_draft(
        user=current_user,
        title=draft_in.title,
        content=draft_in.content,
        community_id=draft_in.community_id,
        attachment_ids=draft_in.attachment_ids
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/drafts", response_model=draft_schemas.PaginatedDraftResponse, summary="获取草稿列表")
async def get_drafts(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的草稿列表（分页）"""
    return await draft_service.get_user_drafts(
        user=current_user,
        skip=skip,
        limit=limit
    )


@router.get("/drafts/{draft_id}", response_model=draft_schemas.DraftOut, summary="获取草稿详情")
async def get_draft_detail(
    draft_id: int,
    current_user: User = Depends(get_current_user),
):
    """获取草稿详情"""
    result = await draft_service.get_draft_detail(
        draft_id=draft_id,
        user=current_user
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.put("/drafts/{draft_id}", response_model=draft_schemas.DraftOut, summary="更新草稿")
async def update_draft(
    draft_id: int,
    draft_in: draft_schemas.DraftUpdate,
    current_user: User = Depends(get_current_user),
):
    """更新草稿内容"""
    result = await draft_service.update_draft(
        draft_id=draft_id,
        user=current_user,
        title=draft_in.title,
        content=draft_in.content,
        community_id=draft_in.community_id,
        attachment_ids=draft_in.attachment_ids
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.delete("/drafts/{draft_id}", summary="删除草稿")
async def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
):
    """删除草稿"""
    result = await draft_service.delete_draft(
        draft_id=draft_id,
        user=current_user
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
