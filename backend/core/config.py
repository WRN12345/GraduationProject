"""
@Time : 2025.11.18
@Author: wrn
@Des: 配置文件 - 自动加载 .env
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os 


class Settings(BaseSettings):

    DESC: str = "Super后台管理系统接口文档"
    TITLE: str = "Super后台管理系统"
    VERSION: str = "v1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "True"

    # --- JWT 安全配置---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")  # 必须在 .env 中配置
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 默认 7 天
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 默认 30 天

    # --- 管理员配置---
    ADMIN_REGISTER_KEY: str = os.getenv("ADMIN_REGISTER_KEY", "")  # 必须在 .env 中配置

    # --- 数据库与 Redis---
    DB_URL: str = os.getenv("DB_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # --- MinIO 对象存储配置 ---
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "True"
    MINIO_IMAGE_BUCKET: str = os.getenv("MINIO_IMAGE_BUCKET", "superimg")
    MINIO_VIDEO_BUCKET: str = os.getenv("MINIO_VIDEO_BUCKET", "supervideo")
    MINIO_FILE_BUCKET: str = os.getenv("MINIO_FILE_BUCKET", "superfile")
    MINIO_PUBLIC_URL: str = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")

    # --- 跨域配置 ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- Redis 缓存配置 ---
    REDIS_POST_DETAIL_TTL: int = int(os.getenv("REDIS_POST_DETAIL_TTL", "600"))  # 帖子详情缓存 TTL (10分钟)
    REDIS_POST_LIST_TTL: int = int(os.getenv("REDIS_POST_LIST_TTL", "300"))  # 帖子列表缓存 TTL (5分钟)
    REDIS_SYNC_INTERVAL: int = int(os.getenv("REDIS_SYNC_INTERVAL", "60"))  # PG 同步间隔 (秒)
    HOT_VIEW_WEIGHT: int = int(os.getenv("HOT_VIEW_WEIGHT", "1"))  # 浏览权重
    HOT_SHARE_WEIGHT: int = int(os.getenv("HOT_SHARE_WEIGHT", "5"))  # 分享权重
    HOT_VOTE_WEIGHT: int = int(os.getenv("HOT_VOTE_WEIGHT", "10"))  # 投票权重

    # --- 配置加载规则 ---
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# 实例化配置对象
settings = Settings()

# 验证关键配置是否已设置（启动时检查）
def validate_settings():
    """验证关键配置是否已从 .env 加载"""
    errors = []

    if not settings.SECRET_KEY or settings.SECRET_KEY == "default_secret_key_change_me":
        errors.append("SECRET_KEY 未在 .env 中配置或使用了不安全的默认值")

    if not settings.ADMIN_REGISTER_KEY or settings.ADMIN_REGISTER_KEY == "admin_secret_key_change_me":
        errors.append("ADMIN_REGISTER_KEY 未在 .env 中配置或使用了不安全的默认值")

    if not settings.DB_URL:
        errors.append("DB_URL 未在 .env 中配置")

    if not settings.REDIS_URL:
        errors.append("REDIS_URL 未在 .env 中配置")

    if errors:
        error_msg = "配置错误：\n" + "\n".join(f"  ❌ {err}" for err in errors)
        error_msg += "\n\n请检查 .env 文件是否正确配置了所有必需的环境变量。"
        raise ValueError(error_msg)

    return True

# 自动验证配置
try:
    validate_settings()
except ValueError as e:
    import sys
    print(f"\n⚠️  {e}\n", file=sys.stderr)
    # 在开发环境可以选择不退出，但在生产环境应该退出
    if not settings.DEBUG:
        sys.exit(1)

# 调试打印 (仅用于检查配置是否加载成功，生产环境请注释)
if __name__ == "__main__":
    print(f"当前环境: {'开发环境' if settings.DEBUG else '生产环境'}")
    print(f"数据库地址: {settings.DB_URL}")
    print(f"跨域白名单: {settings.CORS_ORIGINS}")