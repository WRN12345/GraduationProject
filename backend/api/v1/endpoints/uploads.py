"""
文件上传路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel

from models.user import User
from models.post_attachment import PostAttachment, AttachmentType
from core.security import get_current_user
from core.minio_service import minio_service

router = APIRouter(prefix="/uploads", tags=["文件上传"])


class UploadResponse(BaseModel):
    """单个文件上传响应"""
    id: int  # 附件 ID
    file_url: str
    file_name: str
    file_size: int
    mime_type: str
    attachment_type: str  # image/video/file


@router.post("/images", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传图片（最大 10MB）"""
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 文件大小限制
    MAX_SIZE = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 10MB")

    # 上传到 MinIO
    url = await minio_service.upload_file(
        file_data=content,
        filename=file.filename or "image",
        content_type=file.content_type
    )

    # 创建附件记录
    attachment = await PostAttachment.create(
        post=None,  # 暂不关联帖子
        attachment_type=AttachmentType.IMAGE,
        file_name=file.filename or "image",
        file_url=url,
        file_size=len(content),
        mime_type=file.content_type,
        uploader=current_user
    )

    return UploadResponse(
        id=attachment.id,
        file_url=url,
        file_name=file.filename or "image",
        file_size=len(content),
        mime_type=file.content_type,
        attachment_type="image"
    )


@router.post("/videos", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传视频（最大 100MB）"""
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="只能上传视频文件")

    MAX_SIZE = 100 * 1024 * 1024  # 100MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="视频大小不能超过 100MB")

    url = await minio_service.upload_file(
        file_data=content,
        filename=file.filename or "video",
        content_type=file.content_type
    )

    # 创建附件记录
    attachment = await PostAttachment.create(
        post=None,
        attachment_type=AttachmentType.VIDEO,
        file_name=file.filename or "video",
        file_url=url,
        file_size=len(content),
        mime_type=file.content_type,
        uploader=current_user
    )

    return UploadResponse(
        id=attachment.id,
        file_url=url,
        file_name=file.filename or "video",
        file_size=len(content),
        mime_type=file.content_type,
        attachment_type="video"
    )


@router.post("/files", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传普通文件（最大 50MB）"""
    MAX_SIZE = 50 * 1024 * 1024  # 50MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")

    url = await minio_service.upload_file(
        file_data=content,
        filename=file.filename or "file",
        content_type=file.content_type or 'application/octet-stream'
    )

    # 创建附件记录
    attachment = await PostAttachment.create(
        post=None,
        attachment_type=AttachmentType.FILE,
        file_name=file.filename or "file",
        file_url=url,
        file_size=len(content),
        mime_type=file.content_type or 'application/octet-stream',
        uploader=current_user
    )

    return UploadResponse(
        id=attachment.id,
        file_url=url,
        file_name=file.filename or "file",
        file_size=len(content),
        mime_type=file.content_type or 'application/octet-stream',
        attachment_type="file"
    )


@router.post("/batch", response_model=List[UploadResponse])
async def upload_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """批量上传文件（自动分类）"""
    results = []

    for file in files:
        content = await file.read()

        # 根据 MIME 类型自动分类
        if file.content_type and file.content_type.startswith('image/'):
            MAX_SIZE = 10 * 1024 * 1024
            attachment_type = AttachmentType.IMAGE
            attachment_type_str = "image"
        elif file.content_type and file.content_type.startswith('video/'):
            MAX_SIZE = 100 * 1024 * 1024
            attachment_type = AttachmentType.VIDEO
            attachment_type_str = "video"
        else:
            MAX_SIZE = 50 * 1024 * 1024
            attachment_type = AttachmentType.FILE
            attachment_type_str = "file"

        if len(content) > MAX_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件 {file.filename} 超出大小限制"
            )

        url = await minio_service.upload_file(
            file_data=content,
            filename=file.filename or "file",
            content_type=file.content_type or 'application/octet-stream'
        )

        # 创建附件记录
        attachment = await PostAttachment.create(
            post=None,
            attachment_type=attachment_type,
            file_name=file.filename or "file",
            file_url=url,
            file_size=len(content),
            mime_type=file.content_type or 'application/octet-stream',
            uploader=current_user
        )

        results.append(UploadResponse(
            id=attachment.id,
            file_url=url,
            file_name=file.filename or "file",
            file_size=len(content),
            mime_type=file.content_type or 'application/octet-stream',
            attachment_type=attachment_type_str
        ))

    return results
