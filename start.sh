#!/bin/bash

# Reddit-like Forum System 启动脚本

echo "======================================"
echo "  Reddit-like Forum System 启动中..."
echo "======================================"

# 激活虚拟环境
source .venv/bin/activate

# 检查数据库连接
echo "检查数据库连接..."
python3 -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgres://postgres:123456@127.0.0.1:5432/super_db'))" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 数据库连接失败！请确保 PostgreSQL 正在运行"
    exit 1
fi
echo "✅ 数据库连接成功"

# 检查 Redis
echo "检查 Redis 连接..."
python3 -c "import redis; r = redis.from_url('redis://127.0.0.1:6379'); r.ping()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Redis 连接失败！请确保 Redis 正在运行（可选）"
else
    echo "✅ Redis 连接成功"
fi

echo ""
echo "======================================"
echo "  启动 FastAPI 服务器"
echo "  访问地址: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo "======================================"
echo ""

# 启动应用
python3 main.py
