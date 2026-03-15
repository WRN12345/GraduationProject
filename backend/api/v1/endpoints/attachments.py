"""
附件访问路由 - 提供 presigned URL
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from models.post_attachment import PostAttachment
from services.attachment_service import attachment_service

router = APIRouter(prefix="/attachments", tags=["附件访问"])


class PresignedUrlResponse(BaseModel):
    """单个 presigned URL 响应"""
    attachment_id: int
    presigned_url: str
    expires_in: int  # 秒数


class BatchPresignedUrlRequest(BaseModel):
    """批量获取请求"""
    attachment_ids: List[int]


class BatchPresignedUrlResponse(BaseModel):
    """批量获取响应"""
    urls: dict[int, str]  # {attachment_id: presigned_url}


@router.get("/{attachment_id}/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(attachment_id: int):
    """
    获取附件的 presigned URL（临时访问链接）

    - 无需认证即可访问（支持公开内容）
    - presigned URL 有效期 24 小时
    - 服务端会缓存生成的 URL（23小时 TTL）
    """
    # 查询附件
    attachment = await PostAttachment.get_or_none(id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")

    # 生成 presigned URL
    presigned_url = await attachment_service.get_presigned_url(
        attachment_id=attachment_id,
        file_url=attachment.file_url
    )

    return PresignedUrlResponse(
        attachment_id=attachment_id,
        presigned_url=presigned_url,
        expires_in=24 * 3600  # 24小时
    )


@router.post("/batch-presigned-urls", response_model=BatchPresignedUrlResponse)
async def batch_get_presigned_urls(request: BatchPresignedUrlRequest):
    """
    批量获取附件的 presigned URLs

    - 优化前端展示时的网络请求
    - 返回 {attachment_id: presigned_url} 字典
    """
    if not request.attachment_ids:
        return BatchPresignedUrlResponse(urls={})

    # 查询附件
    attachments = await PostAttachment.filter(
        id__in=request.attachment_ids
    ).values('id', 'file_url')

    if not attachments:
        raise HTTPException(status_code=404, detail="附件不存在")

    # 批量生成 presigned URLs
    urls = await attachment_service.batch_get_presigned_urls(attachments)

    return BatchPresignedUrlResponse(urls=urls)
