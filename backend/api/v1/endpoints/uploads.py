"""
文件上传路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel

from models.user import User
from core.security import get_current_user
from core.services import upload_service

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
    content = await file.read()
    result = await upload_service.upload_image(
        user=current_user,
        file_data=content,
        filename=file.filename or "image",
        content_type=file.content_type
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/videos", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传视频（最大 100MB）"""
    content = await file.read()
    result = await upload_service.upload_video(
        user=current_user,
        file_data=content,
        filename=file.filename or "video",
        content_type=file.content_type
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/files", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传普通文件（最大 50MB）"""
    content = await file.read()
    result = await upload_service.upload_file(
        user=current_user,
        file_data=content,
        filename=file.filename or "file",
        content_type=file.content_type
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/batch", response_model=List[UploadResponse])
async def upload_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """批量上传文件（自动分类）"""
    # 读取所有文件
    file_data_list = []
    for file in files:
        content = await file.read()
        file_data_list.append((content, file.filename or "file", file.content_type))

    results = await upload_service.batch_upload_files(
        user=current_user,
        files=file_data_list
    )

    # 检查是否有错误
    for result in results:
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

    return results
