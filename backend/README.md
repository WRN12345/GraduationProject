# Super Forum System - 仿 Reddit 社区论坛系统

一个功能完整的 Reddit 风格社区论坛系统，基于 FastAPI + PostgreSQL + Redis 构建。

## 核心功能

### 用户认证系统
- JWT 认证机制（Access Token + Refresh Token）
- Token 刷新和轮换
- 用户注册、登录、登出
- 密码加密存储（bcrypt）

### 内容管理
- 版块（Subreddit）创建与管理
- Markdown 格式帖子发布
- 帖子编辑和软删除
- 评论编辑和软删除
- 无限层级嵌套评论（楼中楼）

### 投票系统
- 帖子点赞/踩（Upvote/Downvote）
- 评论点赞/踩
- 实时分数计算
- 投票变更和取消

### 热度排名
- Reddit 经典热度算法
- 时间衰减机制
- 分数权重计算
- 自动更新热度排名

### 用户系统
- 公开用户资料
- 声望（Karma）系统
- 个人简介
- 用户活动追踪
- 发帖和评论历史

### 全文搜索
- PostgreSQL 全文搜索 + GIN 倒排索引
- 中文分词支持（zhcfg 配置）
- 相关性排序（ts_rank）
- 搜索关键词高亮显示（ts_headline）
- 帖子、评论、用户混合搜索

## 技术栈

- **FastAPI 0.124+** - 现代、快速的 Python Web 框架
- **PostgreSQL 14+** - 关系型数据库
- **Tortoise ORM** - 异步 ORM
- **Redis 7+** - 内存数据库（缓存和热度排行）
- **JWT** - JSON Web Tokens 认证

## 快速开始

### 1. 安装依赖

```bash
cd /root/Super

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**如果安装速度慢，使用国内镜像：**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 数据库配置

**使用现有数据库 `super_db`，只添加新字段，不会影响现有数据。**

```bash
# 执行数据库迁移
PGPASSWORD=123456 psql -h 127.0.0.1 -U postgres -d super_db -f migrate_simple.sql
```

**迁移说明：**
- 使用你现有的 `super_db` 数据库，不会新建
- 只添加新字段，不删除或修改现有数据
- 使用 `IF NOT EXISTS`，安全可重复执行

### 3. 配置环境变量

`.env` 文件已配置好（使用现有数据库）：

### 4. 启动应用

```bash
# 方式1：使用启动脚本
./start.sh

# 方式2：直接运行
python3 main.py
```

### 5. 访问应用

```
本地访问：     http://localhost:8000
API 文档：     http://localhost:8000/docs
Swagger UI：  http://localhost:8000/docs
```

## API 端点

### 认证相关（4个）
- `POST /api/v1/login` - 用户登录（返回 access + refresh token）
- `POST /api/v1/refresh` - 刷新访问令牌
- `POST /api/v1/logout` - 登出
- `POST /api/v1/user` - 用户注册

### 帖子相关（10个）
- `GET /api/v1/posts` - 获取帖子列表
- `GET /api/v1/posts/hot` - 获取热门帖子（按热度排名）
- `GET /api/v1/posts/{id}` - 获取帖子详情
- `POST /api/v1/posts` - 创建帖子
- `PUT /api/v1/posts/{id}` - 编辑帖子
- `PATCH /api/v1/posts/{id}` - 部分编辑帖子
- `DELETE /api/v1/posts/{id}` - 软删除帖子
- `POST /api/v1/posts/{id}/restore` - 恢复已删除帖子
- `PATCH /api/v1/posts/{id}/lock` - 锁定/解锁帖子
- `PATCH /api/v1/posts/{id}/highlight` - 设为/取消精华
- `PATCH /api/v1/posts/{id}/pin` - 置顶/取消置顶

### 评论相关（5个）
- `GET /api/v1/posts/{post_id}/comments` - 获取嵌套评论树
- `POST /api/v1/comments` - 创建评论
- `PUT /api/v1/comments/{id}` - 编辑评论
- `DELETE /api/v1/comments/{id}` - 软删除评论
- `POST /api/v1/comments/{id}/restore` - 恢复已删除评论

### 投票相关（2个）
- `POST /api/v1/vote` - 统一投票接口（帖子和评论）
- `GET /api/v1/comments/{id}/vote` - 获取评论投票状态

### 用户相关（6个）
- `GET /api/v1/users` - 获取当前用户（需认证）
- `PUT /api/v1/users` - 更新个人资料（需认证）
- `GET /api/v1/users/{username}` - 获取公开用户资料
- `GET /api/v1/users/{username}/posts` - 获取用户的帖子
- `GET /api/v1/users/{username}/comments` - 获取用户的评论
- `GET /api/v1/users/{username}/activity` - 获取用户活动汇总

### 搜索相关（5个）
- `GET /api/v1/search/posts` - 全文搜索帖子（中文分词）
- `GET /api/v1/search/comments` - 搜索评论（中文分词）
- `GET /api/v1/search/users` - 搜索用户（用户名/昵称）
- `GET /api/v1/search/all` - 统一搜索（帖子+评论+用户）
- `GET /api/v1/search` - 搜索建议（快速预览）

### 社区相关（2个）
- `GET /api/v1/communities` - 获取社区列表
- `POST /api/v1/communities` - 创建社区

### 社区成员相关（3个）
- `POST /api/v1/communities/{community_id}/join` - 加入社区
- `POST /api/v1/communities/{community_id}/leave` - 退出社区
- `GET /api/v1/communities/{community_id}/members` - 获取社区成员列表

## 快速测试

### 1. 测试应用是否运行

```bash
curl http://localhost:8000/docs
```

### 2. 测试用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "nickname": "测试用户",
    "email": "test@example.com"
  }'
```

### 3. 测试登录

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123456"
```

**保存返回的 `access_token`，后续请求需要使用。**

### 4. 测试创建帖子（需要认证）

```bash
TOKEN="your_access_token_here"

curl -X POST "http://localhost:8000/api/v1/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的第一个帖子",
    "content": "这是一个测试帖子，支持 Markdown 格式。",
    "community_id": 1
  }'
```

### 5. 测试投票

```bash
# 为帖子点赞
curl -X POST "http://localhost:8000/api/v1/vote" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 1, "direction": 1}'
```

### 6. 测试热门帖子

```bash
curl -X GET "http://localhost:8000/api/v1/posts/hot"
```

### 7. 测试搜索

```bash
# 搜索帖子（中文全文搜索）
curl -X GET "http://localhost:8000/api/v1/search/posts?q=Python教程"

# 搜索评论
curl -X GET "http://localhost:8000/api/v1/search/comments?q=数据库"

# 搜索用户
curl -X GET "http://localhost:8000/api/v1/search/users?q=alice"

# 统一搜索（同时搜索帖子、评论、用户）
curl -X GET "http://localhost:8000/api/v1/search/all?q=技术"

# 搜索建议（快速预览）
curl -X GET "http://localhost:8000/api/v1/search?q=FastAPI"
```

## 数据库迁移详解

### 新增字段

**users 表：**
- `karma` - 声望值（帖子和评论获得的点赞总数）
- `bio` - 个人简介（最多 5000 字符）

**posts 表：**
- `hot_rank` - 热度分数（Reddit 算法计算）
- `deleted_at` - 软删除时间戳
- `is_edited` - 是否被编辑过
- `updated_at` - 最后更新时间
- `is_locked` - 是否禁止新增评论
- `is_highlighted` - 是否精华内容
- `is_pinned` - 是否置顶帖子
- `deleted_by_id` - 删除者的用户ID

**comments 表：**
- `upvotes` - 点赞数
- `downvotes` - 踩数
- `score` - 净分数（up - down）
- `deleted_at` - 软删除时间戳
- `is_edited` - 是否被编辑过
- `updated_at` - 最后更新时间

**votes 表：**
- `comment_id` - 支持评论投票（外键）

**communities 表：**
- `member_count` - 成员计数

**memberships 表（新增）：**
- `user_id` - 用户ID
- `community_id` - 社区ID
- `joined_at` - 加入时间
- `role` - 角色（member/moderator/owner）

### 新增索引

为提高查询性能，创建以下索引：
- `idx_posts_hot_rank` - 热度排名索引
- `idx_comments_score` - 评论分数索引
- `idx_users_karma` - 用户声望索引
- 等 10+ 个索引

## 核心算法

### Reddit Hot Ranking

```
hot_score = log10(|score|) + (timestamp / 45000)
```

- `score = upvotes - downvotes`
- `45000` = 12.5 小时（时间衰减常数）
- 新帖和高赞帖都能获得合理排名

### Karma 计算

```
karma = 帖子总点赞数 + 评论总点赞数
```

## Redis 缓存架构

### 数据结构设计

```
# 1. 热度排行榜 (Sorted Set)
hot:posts:global          # 全局热门帖子 ZSET
hot:posts:community:{id}  # 社区热门帖子 ZSET

# 2. 帖子详情缓存 (Hash)
post:detail:{id}          # 帖子完整详情 JSON (TTL: 10分钟)

# 3. 交互计数器 (Hash)
post:interactions:{id}    # 交互计数 (view_count, share_count, upvote_count, downvote_count)
```

### 热度更新流程

```
用户交互 (投票/浏览/分享)
    ↓
Redis: 更新计数器 + 重新计算 hot_rank + 更新 ZSET
    ↓
异步任务: 每分钟批量同步到 PostgreSQL
```

### 热门列表查询流程

```
GET /api/v1/posts/hot
    ↓
Redis: ZREVRANGE hot:posts:global 0 20 (取 top 20 post_ids)
    ↓
Redis: HMGET post:detail:{id} ... (批量取详情，如缓存未命中则查 PG)
    ↓
返回: PaginatedPostResponse
```

### 交互权重配置

| 交互类型 | 权重 | 说明 |
|---------|------|------|
| 投票 | 10 | 权重最高，直接参与 score 计算 |
| 分享 | 5 | 中等权重，反映内容传播度 |
| 浏览 | 1 | 低权重，累计到热度 |

### 热度算法（Redis 版本）

```
hot_score = log10(|score|) + (timestamp / 45000) + (interactions * 0.001)
```

- `score = upvotes - downvotes`
- `45000` = 12.5 小时（时间衰减常数）
- `interactions` 根据权重计算（投票*10 + 分享*5 + 浏览*1）

### 缓存策略

| 场景 | 策略 | TTL |
|------|------|-----|
| 热门列表 ZSET | 永久，实时更新 | 无 |
| 帖子详情 Hash | 缓存失效自动删除 | 10 分钟 |
| 交互计数器 | 永久，定时同步 | 无 |
| 帖子编辑/删除 | 立即失效缓存 | 立即 |

## 项目结构

```
Super/
├── backend/
│   ├── api/
│   │   ├── __init__.py          # FastAPI 应用初始化
│   │   └── v1/
│   │       ├── endpoints/        # API 端点
│   │       │   ├── login.py      # 登录、注册、刷新令牌
│   │       │   ├── user.py       # 用户资料、公开资料
│   │       │   ├── posts.py      # 帖子 CRUD、热度排名
│   │       │   ├── comments.py   # 评论 CRUD、嵌套评论
│   │       │   ├── communities.py# 版块管理
│   │       │   ├── memberships.py# 成员管理
│   │       │   ├── votes.py      # 投票系统
│   │       │   └── search.py     # 全文搜索
│   │       └── __init__.py       # 路由注册
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   ├── security.py          # 认证和安全
│   │   ├── cache.py             # Redis 连接
│   │   ├── redis_service.py     # Redis 服务封装（新增）
│   │   ├── tasks.py             # 异步同步任务（新增）
│   │   ├── permissions.py       # 权限控制
│   │   └── audit.py             # 操作审计
│   ├── models/                   # 数据库模型
│   │   ├── user.py              # 用户模型 + Karma 计算
│   │   ├── post.py              # 帖子模型 + Hot Rank 计算
│   │   ├── comment.py           # 评论模型
│   │   ├── vote.py              # 投票模型
│   │   ├── community.py         # 版块模型
│   │   ├── membership.py        # 成员模型
│   │   └── audit_log.py         # 审计日志模型
│   └── schemas/                  # Pydantic schemas
│       ├── user.py              # 用户相关 schemas
│       ├── post.py              # 帖子相关 schemas
│       ├── comment.py           # 评论相关 schemas
│       ├── vote.py              # 投票相关 schemas
│       ├── community.py         # 版块相关 schemas
│       └── membership.py        # 成员相关 schemas
├── frontend/                     # Vue.js 前端（待开发）
├── main.py                       # 应用入口
├── requirements.txt              # Python 依赖
├── migrate_simple.sql           # 数据库迁移脚本
├── start.sh                     # 启动脚本
└── .env                         # 环境配置
```

## 安全特性

- JWT 认证（Access + Refresh Token）
- Token 刷新和轮换
- 密码 bcrypt 加密
- SQL 注入防护（ORM）
- XSS 防护
- CORS 配置
- 输入验证（Pydantic）
- 权限控制（作者/管理员）
- 操作审计日志

## 待开发功能

- 前端界面（Vue.js 3）
- 实时通知（WebSocket）
- 图片上传
- 私信功能
- 版块管理功能
- 内容审核
- 单元测试和集成测试

## 下一步建议

1. **测试功能** - 使用 Swagger UI (http://localhost:8000/docs) 测试所有 API
2. **开发前端** - 使用 Vue.js 3 连接后端 API
3. **添加测试** - 编写单元测试和集成测试
4. **部署生产** - 如需公网访问，考虑配置 Nginx + HTTPS

## 许可证

本项目仅供学习和参考使用。
