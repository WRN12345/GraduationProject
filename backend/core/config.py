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
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # --- RustFS/S3 对象存储配置 ---
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_IMAGE_BUCKET: str = os.getenv("S3_IMAGE_BUCKET", "superimg")
    S3_VIDEO_BUCKET: str = os.getenv("S3_VIDEO_BUCKET", "supervideo")
    S3_FILE_BUCKET: str = os.getenv("S3_FILE_BUCKET", "superfile")

    # --- 跨域配置 ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- Redis 缓存配置 ---
    REDIS_POST_DETAIL_TTL: int = int(os.getenv("REDIS_POST_DETAIL_TTL", "600"))  # 帖子详情缓存 TTL (10分钟)
    REDIS_POST_LIST_TTL: int = int(os.getenv("REDIS_POST_LIST_TTL", "300"))  # 帖子列表缓存 TTL (5分钟)
    REDIS_SYNC_INTERVAL: int = int(os.getenv("REDIS_SYNC_INTERVAL", "60"))  # PG 同步间隔 (秒)
    # --- 热度算法 V2 配置 ---
    HOT_VOTE_WEIGHT: float = float(os.getenv("HOT_VOTE_WEIGHT", "1.0"))  # 净票数权重（基准）
    HOT_COMMENT_WEIGHT: float = float(os.getenv("HOT_COMMENT_WEIGHT", "1.2"))  # 评论数权重
    HOT_FAV_WEIGHT: float = float(os.getenv("HOT_FAV_WEIGHT", "2.0"))  # 收藏数权重
    HOT_TIME_DECAY: float = float(os.getenv("HOT_TIME_DECAY", "1.8"))  # 时间衰减系数（≈36h 半衰期）
    HOT_PIN_BONUS: float = float(os.getenv("HOT_PIN_BONUS", "5.0"))  # 置顶固定加分
    HOT_FEATURED_BONUS: float = float(os.getenv("HOT_FEATURED_BONUS", "2.0"))  # 精华固定加分

    # --- 投票和收藏同步配置 ---
    VOTE_SYNC_INTERVAL: int = int(os.getenv("VOTE_SYNC_INTERVAL", "300"))  # 投票同步间隔（秒）
    BOOKMARK_SYNC_INTERVAL: int = int(os.getenv("BOOKMARK_SYNC_INTERVAL", "300"))  # 收藏同步间隔（秒）

    # --- 投票 Redis TTL 配置 ---
    REDIS_VOTE_COUNTS_TTL: int = int(os.getenv("REDIS_VOTE_COUNTS_TTL", "3600"))  # 投票计数 TTL (1小时)
    REDIS_USER_VOTE_TTL: int = int(os.getenv("REDIS_USER_VOTE_TTL", "86400"))  # 用户投票记录 TTL (24小时)
    REDIS_VOTERS_LIST_TTL: int = int(os.getenv("REDIS_VOTERS_LIST_TTL", "604800"))  # 投票用户列表 TTL (7天)

    # --- 收藏 Redis TTL 配置 ---
    REDIS_BOOKMARK_COUNT_TTL: int = int(os.getenv("REDIS_BOOKMARK_COUNT_TTL", "3600"))  # 收藏计数 TTL (1小时)
    REDIS_BOOKMARK_DETAILS_TTL: int = int(os.getenv("REDIS_BOOKMARK_DETAILS_TTL", "86400"))  # 收藏详情 TTL (24小时)

    # --- Redis 评论缓存配置 ---
    REDIS_COMMENT_TTL: int = int(os.getenv("REDIS_COMMENT_TTL", "3600"))  # 评论缓存 TTL (1小时)
    REDIS_COMMENT_META_TTL: int = int(os.getenv("REDIS_COMMENT_META_TTL", "600"))  # 评论元数据 TTL (10分钟)

    # --- 数据库重试配置 ---
    DB_RETRY_MAX_ATTEMPTS: int = int(os.getenv("DB_RETRY_MAX_ATTEMPTS", "3"))  # 最大重试次数
    DB_RETRY_BASE_DELAY: float = float(os.getenv("DB_RETRY_BASE_DELAY", "1.0"))  # 基础延迟（秒）
    DB_RETRY_MAX_DELAY: float = float(os.getenv("DB_RETRY_MAX_DELAY", "10.0"))  # 最大延迟（秒）
    DB_HEALTH_CHECK_INTERVAL: int = int(os.getenv("DB_HEALTH_CHECK_INTERVAL", "30"))  # 健康检查间隔（秒）

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