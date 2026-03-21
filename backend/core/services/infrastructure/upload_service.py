"""
@Created on : 2026/3/15
@Author: wrn
@Des: 上传服务 - 文件上传 + 验证
"""
from typing import List, Tuple
from models.user import User
from models.post_attachment import PostAttachment, AttachmentType
from core.services.infrastructure.rustfs_service import rustfs_service
import logging

logger = logging.getLogger(__name__)


class UploadService:
    """上传服务 - 文件上传 + 验证"""

    # 文件大小限制
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FILE_SIZE = 50 * 1024 * 1024   # 50MB

    async def upload_image(
        self,
        user: User,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> dict:
        """
        上传图片

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
        if len(file_data) > self.MAX_IMAGE_SIZE:
            return {"error": "图片大小不能超过 10MB"}

        # 上传到 RustFS
        url = await rustfs_service.upload_file(
            file_data=file_data,
            filename=filename or "image",
            content_type=content_type
        )

        # 创建附件记录
        attachment = await PostAttachment.create(
            post=None,
            attachment_type=AttachmentType.IMAGE,
            file_name=filename or "image",
            file_url=url,
            file_size=len(file_data),
            mime_type=content_type,
            uploader=user
        )

        return {
            "id": attachment.id,
            "file_url": url,
            "file_name": filename or "image",
            "file_size": len(file_data),
            "mime_type": content_type,
            "attachment_type": "image"
        }

    async def upload_video(
        self,
        user: User,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> dict:
        """
        上传视频

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
        if not content_type or not content_type.startswith('video/'):
            return {"error": "只能上传视频文件"}

        if len(file_data) > self.MAX_VIDEO_SIZE:
            return {"error": "视频大小不能超过 100MB"}

        url = await rustfs_service.upload_file(
            file_data=file_data,
            filename=filename or "video",
            content_type=content_type
        )

        attachment = await PostAttachment.create(
            post=None,
            attachment_type=AttachmentType.VIDEO,
            file_name=filename or "video",
            file_url=url,
            file_size=len(file_data),
            mime_type=content_type,
            uploader=user
        )

        return {
            "id": attachment.id,
            "file_url": url,
            "file_name": filename or "video",
            "file_size": len(file_data),
            "mime_type": content_type,
            "attachment_type": "video"
        }

    async def upload_file(
        self,
        user: User,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> dict:
        """
        上传普通文件

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
        if len(file_data) > self.MAX_FILE_SIZE:
            return {"error": "文件大小不能超过 50MB"}

        url = await rustfs_service.upload_file(
            file_data=file_data,
            filename=filename or "file",
            content_type=content_type or 'application/octet-stream'
        )

        attachment = await PostAttachment.create(
            post=None,
            attachment_type=AttachmentType.FILE,
            file_name=filename or "file",
            file_url=url,
            file_size=len(file_data),
            mime_type=content_type or 'application/octet-stream',
            uploader=user
        )

        return {
            "id": attachment.id,
            "file_url": url,
            "file_name": filename or "file",
            "file_size": len(file_data),
            "mime_type": content_type or 'application/octet-stream',
            "attachment_type": "file"
        }

    async def batch_upload_files(
        self,
        user: User,
        files: List[Tuple[bytes, str, str]]
    ) -> List[dict]:
        """
        批量上传文件（自动分类）

        Args:
            user: 当前用户
            files: 文件列表 [(file_data, filename, content_type), ...]

        Returns:
            List[dict]: 上传结果列表
        """
        results = []

        for file_data, filename, content_type in files:
            # 根据 MIME 类型自动分类
            if content_type and content_type.startswith('image/'):
                MAX_SIZE = self.MAX_IMAGE_SIZE
                attachment_type = AttachmentType.IMAGE
                attachment_type_str = "image"
            elif content_type and content_type.startswith('video/'):
                MAX_SIZE = self.MAX_VIDEO_SIZE
                attachment_type = AttachmentType.VIDEO
                attachment_type_str = "video"
            else:
                MAX_SIZE = self.MAX_FILE_SIZE
                attachment_type = AttachmentType.FILE
                attachment_type_str = "file"

            if len(file_data) > MAX_SIZE:
                results.append({
                    "error": f"文件 {filename} 超出大小限制"
                })
                continue

            url = await rustfs_service.upload_file(
                file_data=file_data,
                filename=filename or "file",
                content_type=content_type or 'application/octet-stream'
            )

            attachment = await PostAttachment.create(
                post=None,
                attachment_type=attachment_type,
                file_name=filename or "file",
                file_url=url,
                file_size=len(file_data),
                mime_type=content_type or 'application/octet-stream',
                uploader=user
            )

            results.append({
                "id": attachment.id,
                "file_url": url,
                "file_name": filename or "file",
                "file_size": len(file_data),
                "mime_type": content_type or 'application/octet-stream',
                "attachment_type": attachment_type_str
            })

        return results


# 导出服务实例
upload_service = UploadService()

__all__ = ["UploadService", "upload_service"]
