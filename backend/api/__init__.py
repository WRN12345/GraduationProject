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

    # ✅ 加入保活配置
    app.state.redis = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_keepalive=True,
        socket_connect_timeout=5,
        socket_timeout=10,
        retry_on_timeout=True,
        health_check_interval=30,  # 每30秒自动PING，防止NAT断开
    )
    print("Redis 连接成功")

    # 初始化 RustFS 客户端
    from core.services.infrastructure.rustfs_service import rustfs_service
    rustfs_service.initialize()
    await rustfs_service.ensure_buckets()
    print("RustFS 连接成功，Bucket 检查完成")

    # 启动后台同步任务
    from core.tasks.tasks import start_background_tasks
    await start_background_tasks()

    # 启动时初始化热门数据（如果 Redis 中没有数据）
    from core.tasks.tasks import initialize_hot_ranks
    await initialize_hot_ranks()

    # 启动投票和收藏同步任务
    from core.tasks.sync_tasks import start_sync_tasks
    await start_sync_tasks()

    # 启动统计同步任务
    from core.tasks.stats_tasks import start_stats_tasks
    await start_stats_tasks()

    yield # 应用运行期间

    # [关闭时执行]
    await app.state.redis.aclose()
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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Tortoise ORM 配置导出（供 Aerich 使用）---
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "database": settings.DB_NAME,
                "minsize": 2,
                "maxsize": 10,
                "max_inactive_connection_lifetime": 300,
                "server_settings": {
                    "tcp_keepalives_idle": "60",
                    "tcp_keepalives_interval": "10",
                    "tcp_keepalives_count": "5",
                }
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.vote",
                "models.comment",
                "models.community",
                "models.post",
                "models.post_attachment",
                "models.membership",
                "models.bookmark",
                "models.audit_log",
                "models.draft",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}

# --- 数据库注册 ---
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # 使用 Aerich 管理迁移，不再自动生成 schemas
    add_exception_handlers=True,
)

