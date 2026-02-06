import asyncio
import sys
from uvicorn import run
from api import app
from core.config import settings

# 导出 app 供 uvicorn 使用
__all__ = ["app"]


async def check_database():
    """检查数据库连接"""
    try:
        import asyncpg
        await asyncio.sleep(0.1)  # 给数据库一点启动时间
        conn = await asyncpg.connect(settings.DB_URL)
        await conn.close()
        return True
    except Exception as e:
        return False


def check_redis():
    """检查 Redis 连接"""
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return True
    except Exception:
        return False


async def startup_checks():
    """启动前检查所有依赖服务"""
    print("=" * 50)
    print("  Reddit-like Forum System 启动中...")
    print("=" * 50)
    print()

    # 检查数据库
    print("📡 检查数据库连接...")
    db_ok = await check_database()
    if db_ok:
        print("✅ 数据库连接成功")
    else:
        print("❌ 数据库连接失败！请确保 PostgreSQL 正在运行")
        print(f"   连接地址: {settings.DB_URL}")
        sys.exit(1)

    # 检查 Redis
    print()
    print("📡 检查 Redis 连接...")
    redis_ok = check_redis()
    if redis_ok:
        print("✅ Redis 连接成功")
    else:
        print("⚠️  Redis 连接失败！请确保 Redis 正在运行（可选）")
        print("   部分功能（缓存）将不可用")

    print()
    print("=" * 50)
    print("  启动 FastAPI 服务器")
    print(f"  访问地址: http://localhost:8000")
    print(f"  API 文档: http://localhost:8000/docs")
    print("=" * 50)
    print()


if __name__ == "__main__":
    # 运行启动检查
    asyncio.run(startup_checks())

    # 启动应用
    run("main:app", host="0.0.0.0", port=8000, reload=True)
