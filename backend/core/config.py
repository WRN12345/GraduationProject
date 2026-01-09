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
    DEBUG: bool = False

    # --- JWT 安全配置 ---

    SECRET_KEY: str = "default_secret_key_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30天

    # --- 数据库与 Redis---
    DB_URL: str = os.getenv("DB_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")

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

# 调试打印 (仅用于检查配置是否加载成功，生产环境请注释)
if __name__ == "__main__":
    print(f"当前环境: {'开发环境' if settings.DEBUG else '生产环境'}")
    print(f"数据库地址: {settings.DB_URL}")
    print(f"跨域白名单: {settings.CORS_ORIGINS}")