import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import redis.asyncio as redis 
from backend.core.config import settings
from .v1 import v1

# --- 定义生命周期---
@asynccontextmanager

async def lifespan(app: FastAPI):

    # 初始化 Redis 连接池
    app.state.redis = await redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    print("Redis 连接成功")

    # 启动后台同步任务
    from backend.core.tasks import start_background_tasks
    await start_background_tasks()

    yield # 应用运行期间

    # [关闭时执行]
    await app.state.redis.close()
    print("Redis 连接关闭")

# --- 初始化 APP ---
app = FastAPI(
    description=settings.DESC,
    title=settings.TITLE,
    version=settings.VERSION,
    lifespan=lifespan # 注入生命周期
)


# --- 注册路由 ---
app.include_router(v1, prefix="/api")


# --- CORS 配置 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 使用配置文件中的来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---  数据库注册 (主从配置) ---
register_tortoise(
    app,
    db_url=settings.DB_MASTER_URL,  # 默认连接（主库）
    modules={"models": ["backend.models.user", "backend.models.movies", "backend.models.vote", "backend.models.comment", "backend.models.community", "backend.models.post", "backend.models.membership", "backend.models.audit_log"]},
    generate_schemas=False,  # 使用 Aerich 管理迁移，不再自动生成 schemas
    add_exception_handlers=True,
)

# --- Tortoise ORM 配置导出（供 Aerich 使用）---
TORTOISE_ORM = {
    "connections": {
        "master": settings.DB_MASTER_URL,      # 主库连接
        "replica": settings.DB_REPLICA_URL,    # 从库连接
        "default": settings.DB_MASTER_URL,     # 默认连接（兼容性）
    },
    "apps": {
        "models": {
            "models": [
                "backend.models.user",
                "backend.models.movies",
                "backend.models.vote",
                "backend.models.comment",
                "backend.models.community",
                "backend.models.post",
                "backend.models.membership",
                "backend.models.audit_log",
            ],
            "default_connection": "master",  # 模型默认使用主库
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}