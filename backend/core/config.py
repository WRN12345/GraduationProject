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

    # --- JWT 安全配置（从 .env 读取，不暴露密钥）---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")  # 必须在 .env 中配置
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # 默认 30 分钟
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 默认 30 天

    # --- 管理员配置（从 .env 读取，不暴露密钥）---
    ADMIN_REGISTER_KEY: str = os.getenv("ADMIN_REGISTER_KEY", "")  # 必须在 .env 中配置

    # --- 数据库与 Redis（从 .env 读取，不暴露密码）---
    DB_URL: str = os.getenv("DB_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # --- 跨域配置 ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- 配置加载规则 ---
    model_config = SettingsConfigDict(
        env_file=".env",
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