"""
帖子附件模型
"""
from tortoise import models, fields
from enum import Enum


class AttachmentType(str, Enum):
    """附件类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"


class PostAttachment(models.Model):
    """帖子附件"""
    id = fields.IntField(pk=True)

    # 关联帖子(一对多)
    post = fields.ForeignKeyField(
        'models.Post',
        related_name='attachments',
        on_delete=fields.CASCADE,
        null=True  # 允许为空，上传时暂不关联帖子
    )

    # 附件信息
    attachment_type = fields.CharEnumField(AttachmentType, max_length=10)
    file_name = fields.CharField(max_length=255)  # 原始文件名
    file_url = fields.CharField(max_length=1024)  # MinIO URL
    file_size = fields.BigIntField()  # 文件大小(字节)
    mime_type = fields.CharField(max_length=100)  # MIME 类型

    # 上传者信息
    uploader = fields.ForeignKeyField(
        'models.User',
        related_name='uploaded_attachments',
        on_delete=fields.SET_NULL,
        null=True
    )

    # 附件顺序(用于排序显示)
    sort_order = fields.IntField(default=0)

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_attachments"
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return f"{self.attachment_type}: {self.file_name}"


__all__ = ["PostAttachment", "AttachmentType"]
