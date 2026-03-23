"""
@Created on : 2026/3/15
@Author: wrn
@Des: 上传服务 - 文件上传 + 验证
"""
import os
import asyncio
import tempfile
from typing import List, Tuple
from models.user import User
from models.post_attachment import PostAttachment, AttachmentType
from core.services.infrastructure.rustfs_service import rustfs_service
import logging

logger = logging.getLogger(__name__)


async def _convert_to_h264(file_data: bytes) -> bytes:
    """
    将视频转码为 H.264，确保浏览器兼容
    支持微信 H.265/HEVC 视频
    """
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_file:
        input_file.write(file_data)
        input_path = input_file.name

    output_path = input_path.replace('.mp4', '_h264.mp4')

    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',          # 视频转 H.264
            '-c:a', 'aac',              # 音频转 AAC
            '-movflags', '+faststart',  # 支持网页流式播放
            '-preset', 'fast',          # 转码速度（fast/medium/slow）
            '-crf', '23',               # 质量（18-28，越小越清晰）
            '-y',                       # 覆盖输出
            output_path
        ]

        # 异步执行 ffmpeg，不阻塞事件循环
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)

        if process.returncode != 0:
            logger.warning(f"ffmpeg 转码失败，使用原始文件: {stderr.decode()}")
            return file_data  # 转码失败则上传原始文件

        with open(output_path, 'rb') as f:
            return f.read()

    except asyncio.TimeoutError:
        logger.warning("ffmpeg 转码超时，使用原始文件")
        return file_data
    except Exception as e:
        logger.warning(f"转码异常，使用原始文件: {e}")
        return file_data
    finally:
        # 清理临时文件
        for path in [input_path, output_path]:
            try:
                os.unlink(path)
            except Exception:
                pass


class UploadService:
    """上传服务 - 文件上传 + 验证"""

    MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FILE_SIZE = 50 * 1024 * 1024    # 50MB

    async def upload_image(self, user, file_data, filename, content_type):
        # 不变，保持原样
        if not content_type or not content_type.startswith('image/'):
            return {"error": "只能上传图片文件"}
        if len(file_data) > self.MAX_IMAGE_SIZE:
            return {"error": "图片大小不能超过 10MB"}

        url = await rustfs_service.upload_file(
            file_data=file_data, filename=filename or "image", content_type=content_type
        )
        attachment = await PostAttachment.create(
            post=None, attachment_type=AttachmentType.IMAGE,
            file_name=filename or "image", file_url=url,
            file_size=len(file_data), mime_type=content_type, uploader=user
        )
        return {
            "id": attachment.id, "file_url": url,
            "file_name": filename or "image", "file_size": len(file_data),
            "mime_type": content_type, "attachment_type": "image"
        }

    async def upload_video(self, user, file_data, filename, content_type):
        if not content_type or not content_type.startswith('video/'):
            return {"error": "只能上传视频文件"}
        if len(file_data) > self.MAX_VIDEO_SIZE:
            return {"error": "视频大小不能超过 100MB"}

        # ✅ 自动转码为 H.264，兼容所有浏览器
        logger.info(f"开始转码视频: {filename}")
        converted_data = await _convert_to_h264(file_data)
        logger.info(f"转码完成: {filename}, 原始大小={len(file_data)}, 转码后={len(converted_data)}")

        url = await rustfs_service.upload_file(
            file_data=converted_data,
            filename=filename or "video",
            content_type='video/mp4'  # 转码后统一为 mp4
        )
        attachment = await PostAttachment.create(
            post=None, attachment_type=AttachmentType.VIDEO,
            file_name=filename or "video", file_url=url,
            file_size=len(converted_data), mime_type='video/mp4', uploader=user
        )
        return {
            "id": attachment.id, "file_url": url,
            "file_name": filename or "video", "file_size": len(converted_data),
            "mime_type": "video/mp4", "attachment_type": "video"
        }

    # upload_file 和 batch_upload_files 保持原样不变
    async def upload_file(self, user, file_data, filename, content_type):
        if len(file_data) > self.MAX_FILE_SIZE:
            return {"error": "文件大小不能超过 50MB"}
        url = await rustfs_service.upload_file(
            file_data=file_data, filename=filename or "file",
            content_type=content_type or 'application/octet-stream'
        )
        attachment = await PostAttachment.create(
            post=None, attachment_type=AttachmentType.FILE,
            file_name=filename or "file", file_url=url,
            file_size=len(file_data), mime_type=content_type or 'application/octet-stream',
            uploader=user
        )
        return {
            "id": attachment.id, "file_url": url,
            "file_name": filename or "file", "file_size": len(file_data),
            "mime_type": content_type or 'application/octet-stream', "attachment_type": "file"
        }

    async def batch_upload_files(self, user, files):
        results = []
        for file_data, filename, content_type in files:
            if content_type and content_type.startswith('image/'):
                result = await self.upload_image(user, file_data, filename, content_type)
            elif content_type and content_type.startswith('video/'):
                result = await self.upload_video(user, file_data, filename, content_type)
            else:
                result = await self.upload_file(user, file_data, filename, content_type)
            results.append(result)
        return results


upload_service = UploadService()
__all__ = ["UploadService", "upload_service"]