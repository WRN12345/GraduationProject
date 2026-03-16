"""
MinIO 对象存储服务
"""
from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException
import io
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional
from core.config import settings


class MinioService:
    """MinIO 服务单例"""

    def __init__(self):
        self.client: Optional[Minio] = None
        self._initialized = False

    def initialize(self):
        """初始化 MinIO 客户端"""
        try:
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
                region=settings.MINIO_REGION
            )
            # 测试连接
            self.client.list_buckets()
            self._initialized = True
            return self
        except Exception as e:
            print(f"⚠️  MinIO 初始化失败: {e}")
            print(f"   请检查 MinIO 服务是否正常运行")
            print(f"   Endpoint: {settings.MINIO_ENDPOINT}")
            self._initialized = False
            return self

    async def ensure_buckets(self):
        """确保所有必需的 bucket 都存在"""
        if not self._initialized:
            print("⚠️  MinIO 未初始化，跳过 bucket 检查")
            return

        buckets = [
            settings.MINIO_IMAGE_BUCKET,
            settings.MINIO_VIDEO_BUCKET,
            settings.MINIO_FILE_BUCKET
        ]

        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    print(f"📦 创建 bucket: {bucket}")
                    self.client.make_bucket(bucket)

                    # 设置公共读取策略
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{bucket}/*"]
                            }
                        ]
                    }
                    self.client.set_bucket_policy(bucket, json.dumps(policy))
                    print(f"✅ bucket {bucket} 创建成功并设置公共读取策略")
                else:
                    print(f"✅ bucket {bucket} 已存在")
            except S3Error as e:
                print(f"⚠️  bucket {bucket} 操作失败: {e}")
                print(f"   请确保 MinIO 凭证配置正确")
            except Exception as e:
                print(f"⚠️  bucket {bucket} 操作异常: {e}")

    def get_bucket_by_mime(self, mime_type: str) -> str:
        """根据 MIME 类型返回对应的 bucket"""
        if mime_type.startswith('image/'):
            return settings.MINIO_IMAGE_BUCKET
        elif mime_type.startswith('video/'):
            return settings.MINIO_VIDEO_BUCKET
        else:
            return settings.MINIO_FILE_BUCKET

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        bucket: Optional[str] = None
    ) -> str:
        """
        上传文件到 MinIO

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            content_type: MIME 类型
            bucket: 指定 bucket(可选,默认根据 MIME 自动选择)

        Returns:
            公共访问 URL
        """
        if not self._initialized:
            raise HTTPException(status_code=503, detail="MinIO 服务未初始化")

        if bucket is None:
            bucket = self.get_bucket_by_mime(content_type)

        # 生成唯一文件名: timestamp_uuid + 原始扩展名
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        unique_name = f"{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}.{ext}"

        # 上传文件
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=unique_name,
                data=io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

        # 返回公共访问 URL
        return f"{settings.MINIO_PUBLIC_URL}/{bucket}/{unique_name}"

    async def delete_file(self, url: str) -> bool:
        """
        从 MinIO 删除文件

        Args:
            url: 文件的完整 URL

        Returns:
            是否成功删除
        """
        if not self._initialized:
            return False

        try:
            # 解析 URL: http://localhost:9000/bucket/filename
            parts = url.replace(f"{settings.MINIO_PUBLIC_URL}/", "").split('/', 1)
            if len(parts) == 2:
                bucket, object_name = parts
                self.client.remove_object(bucket, object_name)
                return True
        except Exception as e:
            # 记录错误但不抛出异常
            print(f"删除文件失败: {e}")
        return False

    async def generate_presigned_url(
        self,
        url: str,
        expires: timedelta = timedelta(hours=24)
    ) -> str:
        """
        根据存储的 URL 生成 presigned URL（临时访问链接）

        Args:
            url: 文件的公共访问 URL
            expires: 过期时间（默认24小时）

        Returns:
            presigned URL
        """
        if not self._initialized:
            raise HTTPException(status_code=503, detail="MinIO 服务未初始化")

        try:
            # 解析 URL: http://localhost:9000/bucket/filename
            parts = url.replace(f"{settings.MINIO_PUBLIC_URL}/", "").split('/', 1)
            if len(parts) != 2:
                raise ValueError(f"无效的 MinIO URL 格式: {url}")

            bucket, object_name = parts

            # 生成 presigned URL
            presigned_url = self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=expires
            )

            # 替换 base URL 为 MINIO_PUBLIC_URL（让前端可以访问）
            # presigned URL 使用 MINIO_ENDPOINT，需要替换为 MINIO_PUBLIC_URL
            endpoint_base = f"http://{settings.MINIO_ENDPOINT}"
            if settings.MINIO_SECURE:
                endpoint_base = f"https://{settings.MINIO_ENDPOINT}"

            presigned_url = presigned_url.replace(endpoint_base, settings.MINIO_PUBLIC_URL)

            return presigned_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成临时链接失败: {str(e)}")

    async def batch_generate_presigned_urls(
        self,
        urls: list[str],
        expires: timedelta = timedelta(hours=24)
    ) -> dict[str, str]:
        """
        批量生成 presigned URLs

        Args:
            urls: 文件 URL 列表
            expires: 过期时间

        Returns:
            {original_url: presigned_url} 字典
        """
        result = {}
        for url in urls:
            try:
                result[url] = await self.generate_presigned_url(url, expires)
            except Exception as e:
                # 失败时保留原 URL
                result[url] = url
                print(f"生成 presigned URL 失败: {url}, 错误: {e}")
        return result


# 全局单例
minio_service = MinioService()
