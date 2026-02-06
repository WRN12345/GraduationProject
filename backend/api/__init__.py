import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import redis.asyncio as redis 
from core.config import settings
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
    from core.tasks import start_background_tasks
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


# ---  数据库注册 (Pgpool 中间件) ---
register_tortoise(
    app,
    db_url=settings.DB_URL,  # Pgpool 连接
    modules={"models": ["models.user", "models.movies", "models.vote", "models.comment", "models.community", "models.post", "models.membership", "models.audit_log"]},
    generate_schemas=False,  # 使用 Aerich 管理迁移，不再自动生成 schemas
    add_exception_handlers=True,
)

# --- Tortoise ORM 配置导出（供 Aerich 使用）---
TORTOISE_ORM = {
    "connections": {
        "default": settings.DB_URL,
    },
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.movies",
                "models.vote",
                "models.comment",
                "models.community",
                "models.post",
                "models.membership",
                "models.audit_log",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}