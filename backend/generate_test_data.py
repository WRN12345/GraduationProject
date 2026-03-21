"""
测试数据生成脚本
生成社区、帖子、评论等测试数据
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
import random

# 数据库配置
DB_URL = "postgres://postgres:123456@43.161.219.202:5432/super_db"

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
    {"name": "区块链", "description": "以太坊、比特币、Web3技术"},
    {"name": "网络安全", "description": "渗透测试、安全加固、加密技术"},
    {"name": "数据分析", "description": "大数据、可视化、BI分析"},
    {"name": "嵌入式开发", "description": "Arduino、Raspberry Pi、物联网"},
    {"name": "软件工程", "description": "架构设计、设计模式、项目管理"},
    {"name": "开源项目", "description": "贡献开源项目、GitHub技巧"},
    {"name": "程序员职场", "description": "面试技巧、职业发展、职场经验"},
    {"name": "Linux", "description": "Linux系统管理、Shell脚本"},
    {"name": "前端框架", "description": "React、Vue、Angular框架讨论"},
    {"name": "后端架构", "description": "微服务、分布式系统、高并发"},
    {"name": "人工智能", "description": "NLP、计算机视觉、强化学习"},
    {"name": "量化交易", "description": "量化投资、算法交易、金融科技"},
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
    "MySQL 索引优化实战",
    "Nginx 反向代理配置详解",
    "MongoDB 分片集群部署",
    "Elasticsearch 全文搜索优化",
    "RabbitMQ 消息队列实战",
    "Git 高级操作技巧",
    "VSCode 插件推荐",
    "Docker Compose 多容器编排",
    "Prometheus+Grafana 监控部署",
    "GitLab CI/CD 流水线配置",
    "Vim 高级使用技巧",
    "SSH 安全配置指南",
    "AWS EC2 实例类型选择",
    "Azure Functions 无服务器开发",
    "GCP BigQuery 数据分析",
    "TensorFlow 2.x 迁移指南",
    "PyTorch 动态图 vs 静态图",
    "Transformer 模型解析",
    "BERT 预训练模型应用",
    "目标检测 YOLO 系列对比",
    "强化学习 DQN 算法实现",
    "CNN 卷积神经网络详解",
    "LSTM 时序预测实战",
    "OpenCV 图像处理入门",
    "scikit-learn 机器学习实战",
    "Pandas 数据处理技巧",
    "NumPy 数组操作进阶",
    "Matplotlib 数据可视化",
    "区块链共识机制解析",
    "Solidity 智能合约开发",
    "Web3.js 以太坊交互",
    "NFT 铸造与交易原理",
    "Metamask 钱包配置指南",
    "SQL 注入防御实战",
    "XSS 攻击与防御",
    "CSRF 令牌验证机制",
    "OAuth2.0 授权流程",
    "JWT Token 安全最佳实践",
    "Wireshark 网络抓包分析",
    "Kali Linux 渗透测试工具",
    "加密算法 AES/RSA 详解",
    "数字签名与证书",
    "零信任安全架构",
    "Splunk 日志分析实战",
    "Kafka 大数据流处理",
    "Hadoop HDFS 分布式存储",
    "Spark 内存计算引擎",
    "Flink 实时流处理",
    "Arduinosensor 数据采集",
    "Raspberry Pi 家庭服务器",
    "ESP32 WiFi 开发",
    "MQTT物联网协议",
    "5G 技术原理解析",
    "设计模式 SOLID 原则",
    "DDD 领域驱动设计",
    "TDD 测试驱动开发",
    "Clean Code 代码整洁之道",
    "重构改善既有代码",
    "敏捷开发 Scrum 流程",
    "JIRA 项目管理配置",
    "SonarQube 代码质量管理",
    "Linux 性能调优",
    "Bash 脚本自动化",
    "Ansible 配置管理",
    "Terraform 基础设施即代码",
    "Vagrant 开发环境管理",
    "Webpack 构建优化",
    "Babel 转码器配置",
    "ESLint+Prettier 代码规范",
    "npm 包发布流程",
    "Yarn vs pnpm 对比",
    "Next.js SSR 全栈开发",
    "Nuxt.js Vue SSR 框架",
    "Svelte 响应式框架",
    "Tailwind CSS 实用指南",
    "Material UI 组件库",
    "Ant Design Vue 使用",
    "Node.js 事件循环机制",
    "Express 中间件开发",
    "NestJS 模块化架构",
    "Django REST Framework",
    "Spring Boot 微服务",
    "gRPC 服务通信",
    "OAuth2 微服务安全",
    "分布式事务解决方案",
    "CAP 定理与 BASE 理论",
    "Redis 集群高可用",
    "负载均衡算法",
    "CDN 加速原理",
    "HTTP/3 QUIC 协议",
    "WebSocket 实时通信",
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
    """# 实战经验总结

## 项目背景

最近做了一个大型项目，遇到了很多坑，记录下来分享给大家。

## 技术选型

经过调研，我们选择了以下技术栈：

- 后端：Node.js + Express
- 数据库：PostgreSQL + Redis
- 缓存：Redis Cluster
- 容器：Docker + K8s

## 经验教训

1. 前期调研很重要
2. 架构设计要考虑扩展性
3. 团队沟通是成功的关键

欢迎评论区交流！""",
    """# 新手入门指南

## 前言

作为一枚新人，写一篇入门指南帮助大家少走弯路。

## 环境配置

首先需要安装必要的开发工具：

```bash
# 安装 Node.js
nvm install 18
nvm use 18

# 安装依赖
npm install
```

## 第一个项目

创建一个简单的 Hello World 项目：

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(3000);
```

## 总结

希望这篇教程能帮到你！

有问题欢迎留言～""",
    """# 性能优化实战

## 背景

最近在优化一个慢查询，响应时间从 3s 降到了 50ms。

## 问题分析

通过 EXPLAIN 分析，发现查询没有命中索引。

## 解决方案

1. 添加复合索引
2. 优化 SQL 语句
3. 引入缓存层

```sql
CREATE INDEX idx_user_post ON posts(user_id, created_at DESC);
```

## 性能对比

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 响应时间 | 3s | 50ms |
| CPU使用率 | 80% | 20% |

## 结论

数据库优化效果显著，建议大家定期做性能分析。""",
    """# 工具推荐

## 编辑器

推荐使用 VSCode，以下是我常用的插件：

- ESLint - 代码检查
- Prettier - 代码格式化
- GitLens - Git 可视化
- Live Server - 本地服务器

## 命令行

- Oh My Zsh - 终端增强
- tldr - 简化 man 手册
- fzf - 模糊搜索

## 设计工具

- Figma - UI 设计
- Excalidraw - 手绘风格图
- Draw.io - 流程图

欢迎补充！""",
    """# 面试经验分享

## 前言

最近面试了十几家公司，总结了一些经验。

## 技术面

### 常考知识点

1. 数据结构与算法
2. 计算机网络
3. 操作系统
4. 数据库原理
5. 设计模式

### 算法题技巧

- 先暴力，再优化
- 边界条件要考虑
- 代码要写完整

## HR面

- 自我介绍
- 项目经验
- 职业规划
- 为什么离职

## 总结

保持好心态，多面试几家积累经验。祝大家都能拿到满意的 offer！""",
    """# 开源项目贡献

## 为什么贡献开源

1. 学习优秀代码
2. 提升个人影响力
3. 社区回馈

## 如何开始

1. 找到感兴趣的项目
2. 从小 bug 开始
3. 阅读 CONTRIBUTING.md
4. 提交 PR

## 注意事项

- 遵守代码规范
- 写好测试用例
- 详细描述问题

欢迎大家入坑开源！""",
    """# 故障排查记录

## 问题现象

服务出现间歇性响应超时。

## 排查过程

1. 查看日志，发现大量慢查询
2. 检查数据库连接池，已达到上限
3. 分析代码，发现连接未正确释放

## 解决方案

```python
# 修复前
def get_data():
    conn = get_connection()
    # 忘记关闭

# 修复后
def get_data():
    with get_connection() as conn:
        # 自动释放
```

## 总结

资源泄漏是大问题，一定要注意。""",
]

USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123", "nickname": "Alice"},
    {"username": "bob", "email": "bob@example.com", "password": "password123", "nickname": "Bob"},
    {"username": "charlie", "email": "charlie@example.com", "password": "password123", "nickname": "Charlie"},
    {"username": "diana", "email": "diana@example.com", "password": "password123", "nickname": "Diana"},
    {"username": "eve", "email": "eve@example.com", "password": "password123", "nickname": "Eve"},
    {"username": "frank", "email": "frank@example.com", "password": "password123", "nickname": "Frank"},
    {"username": "grace", "email": "grace@example.com", "password": "password123", "nickname": "Grace"},
    {"username": "henry", "email": "henry@example.com", "password": "password123", "nickname": "Henry"},
    {"username": "iris", "email": "iris@example.com", "password": "password123", "nickname": "Iris"},
    {"username": "jack", "email": "jack@example.com", "password": "password123", "nickname": "Jack"},
    {"username": "kate", "email": "kate@example.com", "password": "password123", "nickname": "Kate"},
    {"username": "leo", "email": "leo@example.com", "password": "password123", "nickname": "Leo"},
    {"username": "mary", "email": "mary@example.com", "password": "password123", "nickname": "Mary"},
    {"username": "nancy", "email": "nancy@example.com", "password": "password123", "nickname": "Nancy"},
    {"username": "oscar", "email": "oscar@example.com", "password": "password123", "nickname": "Oscar"},
    {"username": "peter", "email": "peter@example.com", "password": "password123", "nickname": "Peter"},
    {"username": "quinn", "email": "quinn@example.com", "password": "password123", "nickname": "Quinn"},
    {"username": "rose", "email": "rose@example.com", "password": "password123", "nickname": "Rose"},
    {"username": "steve", "email": "steve@example.com", "password": "password123", "nickname": "Steve"},
    {"username": "tina", "email": "tina@example.com", "password": "password123", "nickname": "Tina"},
    {"username": "uma", "email": "uma@example.com", "password": "password123", "nickname": "Uma"},
    {"username": "vince", "email": "vince@example.com", "password": "password123", "nickname": "Vince"},
    {"username": "wendy", "email": "wendy@example.com", "password": "password123", "nickname": "Wendy"},
    {"username": "xander", "email": "xander@example.com", "password": "password123", "nickname": "Xander"},
    {"username": "yara", "email": "yara@example.com", "password": "password123", "nickname": "Yara"},
    {"username": "zack", "email": "zack@example.com", "password": "password123", "nickname": "Zack"},
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
            # 每个社区创建 10-20 个帖子
            num_posts = random.randint(10, 20)

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
                if random.random() > 0.2:  # 80% 概率有评论
                    num_comments = random.randint(3, 15)
                    root_comment_ids = []  # 保存根评论ID用于创建回复

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
                            "写得真好，点赞！",
                            "mark一下",
                            "感谢楼主的无私分享",
                            "这个坑我也踩过",
                            "学到了！",
                            "666",
                            "真香定律！",
                            "有点意思",
                            "不明觉厉",
                            "学习了",
                            "感谢感谢！",
                            "mark",
                            "收藏了",
                            "写的很详细",
                            "支持一下",
                            "很实用的技巧",
                            "好评！",
                            "已保存",
                            "不错不错",
                            "厉害！",
                            "干货满满",
                            "学习了",
                            "顶顶顶！",
                            "感谢博主分享",
                            "这个必须收藏",
                            "说的很有道理！",
                            "支持博主！",
                            "学习了，感谢！",
                        ])

                        comment_created_at = created_at + timedelta(
                            hours=random.randint(0, 24),
                            minutes=random.randint(0, 59)
                        )

                        # 决定是根评论还是回复
                        parent_id = None
                        if root_comment_ids and random.random() > 0.6:  # 40%概率是回复
                            parent_id = random.choice(root_comment_ids)
                            # 回复内容
                            comment_content = random.choice([
                                "同意你的观点！",
                                "我来补充一下",
                                "哈哈，笑死",
                                "+1",
                                "确实如此",
                                "我也这么觉得",
                                "有道理",
                                "哈哈太真实了",
                                "笑不活",
                                "233333",
                                "太对了",
                                "附议！",
                                "同意+1",
                                "说到点子上了",
                                "哈哈太逗了",
                            ])

                        comment_id = await conn.fetchval("""
                            INSERT INTO comments (
                                content, post_id, author_id, parent_id,
                                score, upvotes, downvotes,
                                is_edited, created_at, updated_at
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                            RETURNING id
                        """, comment_content, post_id, commenter, parent_id,
                            random.randint(-5, 20),  # score
                            random.randint(0, 15),     # upvotes
                            random.randint(0, 5),      # downvotes
                            False, comment_created_at, comment_created_at)

                        # 保存根评论ID
                        if parent_id is None:
                            root_comment_ids.append(comment_id)

                        # 为部分根评论添加多层回复
                        if parent_id is None and random.random() > 0.7:  # 30%的根评论有回复
                            num_replies = random.randint(1, 3)
                            for _ in range(num_replies):
                                reply_commenter = random.choice(members)['user_id']
                                reply_content = random.choice([
                                    "同意你的观点！",
                                    "我来补充一下",
                                    "哈哈，笑死",
                                    "+1",
                                    "确实如此",
                                    "回复一下",
                                    "有道理",
                                    "说的对",
                                    "附议！",
                                    "说的太好了",
                                ])
                                reply_created_at = comment_created_at + timedelta(
                                    minutes=random.randint(1, 60)
                                )
                                await conn.execute("""
                                    INSERT INTO comments (
                                        content, post_id, author_id, parent_id,
                                        score, upvotes, downvotes,
                                        is_edited, created_at, updated_at
                                    )
                                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                                """, reply_content, post_id, reply_commenter, comment_id,
                                    random.randint(-3, 10),
                                    random.randint(0, 8),
                                    random.randint(0, 3),
                                    False, reply_created_at, reply_created_at)

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
