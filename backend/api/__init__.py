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
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---  数据库注册 ---
register_tortoise(
    app,
    db_url=settings.DB_URL,
    modules={"models": ["backend.models.user", "backend.models.movies", "backend.models.vote", "backend.models.comment", "backend.models.community", "backend.models.post"]},
    generate_schemas=False,  # 使用 Aerich 管理迁移，不再自动生成 schemas
    add_exception_handlers=True,
)

# --- Tortoise ORM 配置导出（供 Aerich 使用）---
TORTOISE_ORM = {
    "connections": {"default": settings.DB_URL},
    "apps": {
        "models": {
            "models": [
                "backend.models.user",
                "backend.models.movies",
                "backend.models.vote",
                "backend.models.comment",
                "backend.models.community",
                "backend.models.post",
            ],
            "default_connection": "default",
        }
    },
}