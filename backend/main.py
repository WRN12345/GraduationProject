"""
Reddit-like Forum System - Main Entry Point
带有完整的启动前检查机制
"""
import asyncio
import sys
import re
from uvicorn import run
from api import app
from core.config import settings


# 导出 app 供 uvicorn 使用
__all__ = ["app"]


# ==================== 检查函数定义 ====================

async def check_database_connection():
    """检查数据库连接 - 增强版"""
    print("📡 检查数据库连接...")
    try:
        import asyncpg
        
        # 尝试连接数据库
        conn = await asyncpg.connect(
            settings.DB_URL,
            timeout=5  # 5秒超时
        )
        
        # 测试查询
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        
        # 提取 PostgreSQL 版本号
        match = re.search(r'PostgreSQL (\d+\.\d+)', version)
        version_str = match.group(1) if match else "未知"
        
        print(f"   ✅ 连接成功 (PostgreSQL {version_str})")
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ 连接失败: {error_msg}")
        return False, f"PostgreSQL 连接失败: {error_msg}"


async def check_database_tables():
    """检查数据库表是否存在"""
    print("   📋 检查数据库表结构...")
    try:
        import asyncpg
        conn = await asyncpg.connect(settings.DB_URL, timeout=5)
        
        # 检查核心表是否存在
        required_tables = [
            'users', 'communities', 'posts', 'comments', 
            'votes', 'bookmarks', 'community_memberships', 'post_attachments'
        ]
        
        existing_tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        existing_table_names = {row['tablename'] for row in existing_tables}
        
        missing_tables = [t for t in required_tables if t not in existing_table_names]
        
        await conn.close()
        
        if missing_tables:
            print(f"   ⚠️  缺少表: {', '.join(missing_tables)}")
            return False, f"缺少表: {', '.join(missing_tables)}"
        
        print(f"   ✅ {len(required_tables)} 个核心表存在")
        return True, None
        
    except Exception as e:
        print(f"   ⚠️  表检查失败: {e}")
        return None, f"表检查失败: {e}"  # None 表示不确定


async def check_redis_connection():
    """检查 Redis 连接 - 增强版"""
    print("📡 检查 Redis 连接...")
    try:
        import redis
        
        r = redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=3,
            socket_timeout=3
        )
        
        # PING 并获取信息
        info = r.info('server')
        redis_version = info.get('redis_version', '未知')
        r.ping()
        
        print(f"   ✅ 连接成功 (Redis {redis_version})")
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ 连接失败: {error_msg}")
        return False, f"Redis 连接失败: {error_msg}"


async def check_redis_cache_sync():
    """检查 Redis 缓存同步状态"""
    print("   🔄 检查缓存同步状态...")
    try:
        import redis.asyncio as aioredis
        
        r = await aioredis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=3,
            socket_timeout=3
        )
        
        # 检查投票同步队列
        from core.services.content.vote_service import vote_service
        post_sync_key = vote_service._get_sync_key("post")
        comment_sync_key = vote_service._get_sync_key("comment")
        
        # 检查收藏同步队列
        from core.services.content.bookmark_service import bookmark_service
        bookmark_sync_key = bookmark_service._get_sync_key()
        
        # 获取待同步数量
        pending_votes = await r.scard(post_sync_key) + await r.scard(comment_sync_key)
        pending_bookmarks = await r.scard(bookmark_sync_key)
        
        await r.aclose()
        
        if pending_votes > 0:
            print(f"   ⚠️  待同步投票数据: {pending_votes} 条")
        else:
            print(f"   ✅ 投票缓存已同步")
            
        if pending_bookmarks > 0:
            print(f"   ⚠️  待同步收藏数据: {pending_bookmarks} 条")
        else:
            print(f"   ✅ 收藏缓存已同步")
        
        return True, None
        
    except Exception as e:
        print(f"   ⚠️  缓存同步检查失败: {e}")
        return None, f"缓存同步检查失败: {e}"


async def check_rustfs_connection():
    """检查 RustFS/S3 对象存储连接"""
    print("📡 检查 RustFS/S3 对象存储...")
    try:
        from minio import Minio
        from minio.error import S3Error
        
        # 解析 endpoint
        endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")
        secure = settings.S3_ENDPOINT.startswith("https://")
        
        client = Minio(
            endpoint=endpoint,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=secure
        )
        
        # 列出 bucket 测试连接
        buckets = client.list_buckets()
        
        # 检查必需的 bucket
        required_buckets = {
            settings.S3_IMAGE_BUCKET,
            settings.S3_VIDEO_BUCKET,
            settings.S3_FILE_BUCKET
        }
        existing_buckets = {b.name for b in buckets}
        missing_buckets = required_buckets - existing_buckets
        
        await asyncio.get_event_loop().run_in_executor(None, lambda: None)  # 异步兼容
        
        if missing_buckets:
            print(f"   ⚠️  缺少 Bucket: {', '.join(missing_buckets)}")
            print(f"   ℹ️  启动时将自动创建")
        
        print(f"   ✅ 连接成功 ({len(existing_buckets)} 个 Bucket)")
        return True, None
        
    except S3Error as e:
        print(f"   ❌ 连接失败: {e}")
        return False, f"S3 连接失败: {e}"
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            print(f"   ❌ 无法连接到 S3 服务: {e}")
            return False, f"S3 服务不可达: {error_msg}"
        print(f"   ⚠️  S3 配置错误: {e}")
        return False, f"S3 配置错误: {error_msg}"


def check_critical_config():
    """检查关键配置项"""
    print("📋 检查关键配置...")
    issues = []
    
    # 检查数据库配置
    if not settings.DB_URL:
        issues.append("DB_URL 未配置")
    
    # 检查 Redis 配置
    if not settings.REDIS_URL:
        issues.append("REDIS_URL 未配置")
    
    # 检查 JWT 密钥
    if not settings.SECRET_KEY:
        issues.append("SECRET_KEY 未配置")
    elif len(settings.SECRET_KEY) < 32:
        issues.append("SECRET_KEY 长度不足（建议32位以上）")
    
    # 检查管理员注册密钥
    if not settings.ADMIN_REGISTER_KEY:
        issues.append("ADMIN_REGISTER_KEY 未配置")
    
    # 检查 S3 配置
    if not settings.S3_ENDPOINT:
        issues.append("S3_ENDPOINT 未配置")
    if not settings.S3_ACCESS_KEY:
        issues.append("S3_ACCESS_KEY 未配置")
    if not settings.S3_SECRET_KEY:
        issues.append("S3_SECRET_KEY 未配置")
    
    if issues:
        print("   ❌ 配置问题:")
        for issue in issues:
            print(f"      - {issue}")
        return False, "; ".join(issues)
    
    print("   ✅ 所有关键配置已填写")
    return True, None


# ==================== 启动检查主函数 ====================

async def startup_checks():
    """启动前检查所有依赖服务 - 完整版"""
    print()
    print("=" * 60)
    print("           Reddit-like Forum System 启动检查")
    print("=" * 60)
    print()
    
    results = {
        "database": {"status": None, "details": None},
        "redis": {"status": None, "details": None},
        "rustfs": {"status": None, "details": None},
        "config": {"status": None, "details": None},
    }
    
    # 1. 检查关键配置
    config_ok, config_msg = check_critical_config()
    results["config"]["status"] = config_ok
    results["config"]["details"] = config_msg
    print()
    
    if not config_ok:
        print("❌ 关键配置缺失，退出启动")
        print(f"   原因: {config_msg}")
        sys.exit(1)
    
    # 2. 检查数据库
    print()
    db_ok, db_msg = await check_database_connection()
    results["database"]["status"] = db_ok
    results["database"]["details"] = db_msg
    
    if db_ok:
        # 检查表结构
        tables_ok, tables_msg = await check_database_tables()
        if tables_ok is False:
            results["database"]["details"] = tables_msg
    print()
    
    # 3. 检查 Redis
    print()
    redis_ok, redis_msg = await check_redis_connection()
    results["redis"]["status"] = redis_ok
    results["redis"]["details"] = redis_msg
    
    if redis_ok:
        # 检查缓存同步状态
        sync_ok, sync_msg = await check_redis_cache_sync()
        # 缓存同步失败不影响启动，只是警告
    print()
    
    # 4. 检查 RustFS/S3
    print()
    rustfs_ok, rustfs_msg = await check_rustfs_connection()
    results["rustfs"]["status"] = rustfs_ok
    results["rustfs"]["details"] = rustfs_msg
    print()
    
    # ==================== 汇总结果 ====================
    print("=" * 60)
    print("                    检查结果汇总")
    print("=" * 60)
    print()
    
    # 数据库
    if results["database"]["status"]:
        print("✅ 数据库: 正常")
    else:
        print("❌ 数据库: 失败")
        if results["database"]["details"]:
            print(f"   {results['database']['details']}")
    print()
    
    # Redis
    if results["redis"]["status"]:
        print("✅ Redis: 正常")
    elif results["redis"]["status"] is False:
        print("❌ Redis: 失败")
        print("   部分功能（缓存）将不可用")
    else:
        print("⚠️  Redis: 状态未知")
    print()
    
    # RustFS/S3
    if results["rustfs"]["status"]:
        print("✅ 对象存储: 正常")
    elif results["rustfs"]["status"] is False:
        print("❌ 对象存储: 失败")
        print("   文件上传功能将不可用")
    else:
        print("⚠️  对象存储: 状态未知")
    print()
    
    # 配置
    if results["config"]["status"]:
        print("✅ 配置: 正常")
    print()
    
    # 判断是否可以启动
    critical_fail = (
        results["database"]["status"] is False or 
        results["config"]["status"] is False
    )
    
    if critical_fail:
        print("=" * 60)
        print("❌ 启动失败 - 请修复上述错误后重试")
        print("=" * 60)
        sys.exit(1)
    
    # 打印启动信息
    print("=" * 60)
    print("  🎉 所有核心检查通过，准备启动服务")
    print()
    print(f"  🌐 访问地址: http://localhost:8000")
    print(f"  📚 API 文档: http://localhost:8000/docs")
    print("=" * 60)
    print()


# ==================== 主入口 ====================

if __name__ == "__main__":
    # 运行启动检查
    asyncio.run(startup_checks())
    
    # 启动应用
    run("main:app", host="0.0.0.0", port=8000, reload=True)
