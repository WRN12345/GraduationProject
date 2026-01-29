"""
测试数据生成脚本
生成社区、帖子、评论等测试数据
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
import random

# 数据库配置
DB_URL = "postgres://postgres:123456@127.0.0.1:5432/super_db"

# 测试数据
COMMUNITIES = [
    {"name": "Python编程", "description": "讨论Python编程相关话题"},
    {"name": "Web开发", "description": "前端、后端、全栈开发讨论"},
    {"name": "机器学习", "description": "AI、ML、深度学习技术交流"},
    {"name": "游戏开发", "description": "游戏设计与开发技术"},
    {"name": "DevOps", "description": "运维、容器化、CI/CD"},
    {"name": "移动开发", "description": "iOS、Android开发"},
    {"name": "数据库技术", "description": "SQL、NoSQL数据库"},
    {"name": "云计算", "description": "AWS、Azure、GCP云服务"},
]

POST_TITLES = [
    "Python 3.13 新特性详解",
    "FastAPI vs Flask：如何选择？",
    "Docker 最佳实践指南",
    "PostgreSQL 性能优化技巧",
    "Redis 缓存策略设计",
    "Kubernetes 入门教程",
    "TypeScript 高级类型技巧",
    "Vue 3 Composition API 实战",
    "React Hooks 深度解析",
    "微服务架构设计模式",
    "GraphQL vs RESTful API",
    "WebAssembly 未来展望",
    "Rust 语言学习路线",
    "Go 语言并发编程",
    "算法与数据结构面试题",
]

POST_CONTENTS = [
    """## 引言

这是一个关于技术的讨论。近年来，随着技术的快速发展，我们需要不断学习新知识。

## 主要内容

1. 基础概念
2. 实战案例
3. 最佳实践
4. 性能优化

## 总结

希望本文对你有所帮助！""",
    """大家好！

今天想和大家分享一些学习经验。在学习过程中，我发现：

- 理论与实践相结合很重要
- 多做项目能加深理解
- 参与开源社区很有帮助

欢迎大家讨论！""",
    """# 技术分享

## 问题背景

在开发过程中，我们经常遇到各种挑战。

## 解决方案

通过研究和实践，我找到了一些解决方案。

### 代码示例

```python
def hello_world():
    print("Hello, World!")
```

希望对大家有帮助！""",
]

USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123", "nickname": "Alice"},
    {"username": "bob", "email": "bob@example.com", "password": "password123", "nickname": "Bob"},
    {"username": "charlie", "email": "charlie@example.com", "password": "password123", "nickname": "Charlie"},
    {"username": "diana", "email": "diana@example.com", "password": "password123", "nickname": "Diana"},
    {"username": "eve", "email": "eve@example.com", "password": "password123", "nickname": "Eve"},
]


async def generate_password_hash(password: str) -> str:
    """生成密码哈希（使用bcrypt，与系统一致）"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # bcrypt 限制密码最大72字节
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


async def create_test_data():
    """创建测试数据"""
    conn = await asyncpg.connect(DB_URL)

    try:
        print("🚀 开始生成测试数据...\n")

        # 1. 创建测试用户
        print("📝 创建测试用户...")
        user_ids = []
        for user in USERS:
            # 检查用户是否已存在
            existing = await conn.fetchval(
                "SELECT id FROM users WHERE username = $1",
                user["username"]
            )
            if existing:
                user_id = existing
                print(f"  ✅ 用户 {user['username']} 已存在")
            else:
                password_hash = await generate_password_hash(user["password"])
                user_id = await conn.fetchval("""
                    INSERT INTO users (username, email, password, nickname, is_active, is_superuser)
                    VALUES ($1, $2, $3, $4, true, false)
                    RETURNING id
                """, user["username"], user["email"], password_hash, user["nickname"])
                print(f"  ✅ 创建用户: {user['username']}")
            user_ids.append(user_id)

        # 获取第一个用户作为主要创建者
        creator_id = user_ids[0]

        # 2. 创建社区
        print("\n🏘️  创建社区...")
        community_ids = []
        for i, community in enumerate(COMMUNITIES):
            # 检查社区是否已存在
            existing = await conn.fetchval(
                "SELECT id FROM communities WHERE name = $1",
                community["name"]
            )
            if existing:
                community_id = existing
                print(f"  ✅ 社区 {community['name']} 已存在")
            else:
                # 轮换使用不同的用户作为创建者
                creator = user_ids[i % len(user_ids)]
                community_id = await conn.fetchval("""
                    INSERT INTO communities (name, description, creator_id, created_at, member_count)
                    VALUES ($1, $2, $3, $4, 0)
                    RETURNING id
                """, community["name"], community["description"], creator, datetime.now())
                print(f"  ✅ 创建社区: {community['name']} (创建者: {USERS[i % len(user_ids)]['username']})")
            community_ids.append(community_id)

        # 3. 为每个社区创建成员关系（群主）
        print("\n👥 创建社区成员关系...")
        for i, community_id in enumerate(community_ids):
            creator = user_ids[i % len(user_ids)]

            # 检查是否已存在成员关系
            existing = await conn.fetchval(
                "SELECT id FROM community_memberships WHERE user_id = $1 AND community_id = $2",
                creator, community_id
            )
            if existing:
                print(f"  ✅ 社区 {COMMUNITIES[i]['name']} 的成员关系已存在")
            else:
                # 创建群主成员记录
                await conn.execute("""
                    INSERT INTO community_memberships (user_id, community_id, role, joined_at, updated_at)
                    VALUES ($1, $2, 2, $3, $4)
                    ON CONFLICT (user_id, community_id) DO NOTHING
                """, creator, community_id, datetime.now(), datetime.now())

                # 更新社区成员计数
                await conn.execute(
                    "UPDATE communities SET member_count = member_count + 1 WHERE id = $1",
                    community_id
                )
                print(f"  ✅ 社区 {COMMUNITIES[i]['name']} - 群主: {USERS[i % len(user_ids)]['username']}")

            # 为其他用户随机加入社区
            for user_id in user_ids:
                if user_id != creator and random.random() > 0.3:  # 70% 概率加入
                    existing = await conn.fetchval(
                        "SELECT id FROM community_memberships WHERE user_id = $1 AND community_id = $2",
                        user_id, community_id
                    )
                    if not existing:
                        await conn.execute("""
                            INSERT INTO community_memberships (user_id, community_id, role, joined_at, updated_at)
                            VALUES ($1, $2, 0, $3, $4)
                            ON CONFLICT (user_id, community_id) DO NOTHING
                        """, user_id, community_id, datetime.now(), datetime.now())
                        await conn.execute(
                            "UPDATE communities SET member_count = member_count + 1 WHERE id = $1",
                            community_id
                        )

        # 4. 创建帖子
        print("\n📰 创建帖子...")
        post_count = 0
        for community_id in community_ids:
            # 每个社区创建 3-8 个帖子
            num_posts = random.randint(3, 8)

            # 获取该社区的成员
            members = await conn.fetch("""
                SELECT user_id FROM community_memberships
                WHERE community_id = $1 AND role >= 0
                ORDER BY RANDOM()
            """, community_id)

            if not members:
                continue

            for _ in range(num_posts):
                author = random.choice(members)['user_id']
                title = random.choice(POST_TITLES)
                content = random.choice(POST_CONTENTS)

                # 生成随机时间（最近30天内）
                created_at = datetime.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )

                post_id = await conn.fetchval("""
                    INSERT INTO posts (
                        title, content, author_id, community_id,
                        score, upvotes, downvotes, hot_rank,
                        is_edited, is_locked, is_highlighted, is_pinned,
                        created_at, updated_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    RETURNING id
                """, title, content, author, community_id,
                    random.randint(-10, 100),  # score
                    random.randint(0, 50),     # upvotes
                    random.randint(0, 10),     # downvotes
                    random.uniform(0, 1000),   # hot_rank
                    False, False, False, False,  # bool fields
                    created_at, created_at)

                post_count += 1

                # 随机为一些帖子添加评论
                if random.random() > 0.5:  # 50% 概率有评论
                    num_comments = random.randint(1, 5)
                    for _ in range(num_comments):
                        commenter = random.choice(members)['user_id']
                        comment_content = random.choice([
                            "很有启发！感谢分享！",
                            "学习了，收藏一下",
                            "请问有更详细的教程吗？",
                            "这个观点很新颖",
                            "我也遇到过类似问题",
                            "期待后续更新",
                            "可以分享一下代码吗？",
                        ])

                        comment_created_at = created_at + timedelta(
                            hours=random.randint(0, 24),
                            minutes=random.randint(0, 59)
                        )

                        await conn.execute("""
                            INSERT INTO comments (
                                content, post_id, author_id,
                                score, upvotes, downvotes,
                                is_edited, created_at, updated_at
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        """, comment_content, post_id, commenter,
                            random.randint(-5, 20),  # score
                            random.randint(0, 15),     # upvotes
                            random.randint(0, 5),      # downvotes
                            False, comment_created_at, comment_created_at)

        print(f"\n✅ 测试数据生成完成！")
        print(f"\n📊 数据统计：")
        print(f"  - 用户数: {len(user_ids)}")
        print(f"  - 社区数: {len(community_ids)}")
        print(f"  - 帖子数: {post_count}")

        # 显示实际数据库统计
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_communities = await conn.fetchval("SELECT COUNT(*) FROM communities")
        total_posts = await conn.fetchval("SELECT COUNT(*) FROM posts WHERE deleted_at IS NULL")
        total_comments = await conn.fetchval("SELECT COUNT(*) FROM comments WHERE deleted_at IS NULL")
        total_memberships = await conn.fetchval("SELECT COUNT(*) FROM community_memberships")

        print(f"\n📈 数据库实际统计：")
        print(f"  - 总用户数: {total_users}")
        print(f"  - 总社区数: {total_communities}")
        print(f"  - 总帖子数: {total_posts}")
        print(f"  - 总评论数: {total_comments}")
        print(f"  - 总成员关系: {total_memberships}")

    finally:
        await conn.close()


async def main():
    """主函数"""
    try:
        await create_test_data()
        print("\n✨ 完成！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
