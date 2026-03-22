# Super Forum System - 仿 Reddit 社区论坛系统

一个功能完整的 Reddit 风格社区论坛系统，基于 FastAPI + Vue 3 + PostgreSQL + Redis 构建。

## 核心功能

### 用户认证系统
- JWT 认证机制（Access Token + Refresh Token）
- Token 刷新和轮换
- Token 黑名单（登出后失效）
- 用户注册、登录、登出
- 密码加密存储（bcrypt）

### 社区管理
- 社区创建与管理
- 创建者自动成为社区拥有者
- 社区成员角色系统（member/moderator/owner）
- 加入/退出社区功能
- 我的社区列表展示
- 社区详情页面
- 发帖时自动加入社区（如果未加入）
- 社区成员管理（封禁/解封用户）
- 社区管理员晋升/降级
- 社区所有权转让
- 社区推荐（根据帖子内容智能推荐）

### 内容管理
- Markdown 格式帖子发布
- 帖子编辑和软删除
- 帖子锁定/解锁
- 帖子置顶/取消置顶
- 精华标记/取消
- 评论编辑和软删除
- 无限层级嵌套评论（楼中楼）
- 动态流（Home Feed）获取

### 投票系统
- 帖子点赞/踩（Upvote/Downvote）
- 评论点赞/踩
- 实时分数计算
- 投票变更和取消
- 批量投票状态查询

### 收藏系统
- 帖子收藏/取消收藏
- 收藏列表管理
- 收藏夹分类和笔记
- 批量检查收藏状态
- 帖子收藏数查询

### 热度排名
- Reddit 经典热度算法
- 时间衰减机制
- 分数权重计算
- Redis 实时热度排行
- 全局热门和社区热门
- 侧边栏热门内容（热门帖子、热门社区、活跃用户）

### 文件上传
- 图片上传（最大 10MB）
- 视频上传（最大 100MB）
- 普通文件上传（最大 50MB）
- 批量文件上传（自动分类）
- 附件 Presigned URL 访问（24小时有效期）
- 批量获取 Presigned URLs

### 用户系统
- 公开用户资料
- 声望（Karma）系统
- 个人简介
- 用户活动追踪
- 发帖和评论历史
- 个人帖子/评论/活动汇总

### 全文搜索
- PostgreSQL 全文搜索 + GIN 倒排索引
- 中文分词支持（zhcfg 配置）
- 相关性排序（ts_rank）
- 搜索关键词高亮显示（ts_headline）
- 帖子、评论、用户混合搜索
- 搜索建议（快速预览）

## 技术栈

### 后端
- **FastAPI 0.104+** - 现代、快速的 Python Web 框架
- **PostgreSQL 14+** - 关系型数据库
- **Tortoise ORM** - 异步 ORM
- **Redis 7+** - 内存数据库（缓存和热度排行）
- **JWT** - JSON Web Tokens 认证
- **Pydantic** - 数据验证和序列化

### 前端
- **Vue 3.5+** - 渐进式 JavaScript 框架
- **TypeScript 5.9+** - 类型安全的 JavaScript
- **Vite 7.2+** - 快速构建工具
- **Element Plus 2.12+** - Vue 3 UI 组件库
- **Pinia 2.3+** - Vue 状态管理
- **Vue Router 4.0+** - 客户端路由
- **OpenAPI Fetch 0.15+** - 类型安全的 API 客户端
- **Lucide Vue Next** - 图标库

## 快速开始

### 1. 安装后端依赖

```bash
cd /root/Super

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend

# 安装依赖
npm install

# 或使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

**如果安装速度慢，使用国内镜像：**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 数据库配置

使用现有数据库 `super_db`，只添加新字段，不会影响现有数据。

```bash
# 执行数据库迁移
PGPASSWORD=123456 psql -h 127.0.0.1 -U postgres -d super_db -f migrate_simple.sql
```

### 4. 配置环境变量

`.env` 文件已配置好（使用现有数据库）

### 5. 启动应用

**后端：**
```bash
# 使用启动脚本
./start.sh

# 或直接运行
python3 main.py
```

**前端：**
```bash
cd frontend

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

### 6. 访问应用

```
后端 API：     http://localhost:8000
API 文档：     http://localhost:8000/docs
前端开发：     http://localhost:5173
```

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
│   │       │   ├── communities.py# 社区管理
│   │       │   ├── memberships.py# 成员管理、封禁、管理员
│   │       │   ├── votes.py      # 投票系统
│   │       │   ├── search.py     # 全文搜索
│   │       │   ├── bookmarks.py  # 收藏系统
│   │       │   ├── uploads.py    # 文件上传
│   │       │   ├── attachments.py# 附件访问
│   │       │   └── hot.py        # 热门内容
│   │       └── __init__.py       # 路由注册
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   ├── security.py          # 认证和安全
│   │   ├── cache.py             # Redis 连接
│   │   ├── permissions.py      # 权限控制
│   │   ├── audit.py             # 操作审计
│   │   ├── tasks/               # 异步任务
│   │   │   ├── sync_tasks.py    # 数据同步任务
│   │   │   ├── stats_tasks.py  # 统计任务
│   │   │   └── tasks.py         # 任务调度
│   │   └── services/            # 业务服务
│   │       ├── auth/            # 认证服务
│   │       ├── content/         # 内容服务
│   │       │   ├── post_service.py
│   │       │   ├── comment_service.py
│   │       │   ├── community_service.py
│   │       │   ├── vote_service.py
│   │       │   ├── bookmark_service.py
│   │       │   ├── hot_content_service.py
│   │       │   └── search_service.py
│   │       └── infrastructure/ # 基础设施服务
│   │           ├── upload_service.py
│   │           ├── attachment_service.py
│   │           └── rustfs_service.py
│   ├── models/                  # 数据库模型
│   │   ├── user.py              # 用户模型 + Karma 计算
│   │   ├── post.py              # 帖子模型 + Hot Rank 计算
│   │   ├── comment.py           # 评论模型
│   │   ├── vote.py              # 投票模型
│   │   ├── community.py         # 社区模型
│   │   ├── membership.py        # 成员模型
│   │   ├── bookmark.py          # 收藏模型
│   │   ├── post_attachment.py   # 附件模型
│   │   └── audit_log.py         # 审计日志模型
│   ├── schemas/                 # Pydantic schemas
│   │   ├── user.py              # 用户相关 schemas
│   │   ├── post.py              # 帖子相关 schemas
│   │   ├── comment.py           # 评论相关 schemas
│   │   ├── vote.py              # 投票相关 schemas
│   │   ├── community.py         # 社区相关 schemas
│   │   ├── membership.py        # 成员相关 schemas
│   │   ├── bookmark.py          # 收藏相关 schemas
│   │   └── hot.py               # 热门内容 schemas
│   └── migrations/              # 数据库迁移
├── frontend/
│   ├── src/
│   │   ├── components/          # 可复用 Vue 组件
│   │   │   ├── Layout.vue       # 主布局
│   │   │   ├── Header.vue       # 导航头部
│   │   │   ├── PostList.vue     # 帖子列表
│   │   │   ├── PostCard.vue     # 帖子卡片
│   │   │   ├── VoteButtons.vue  # 投票按钮
│   │   │   ├── BookmarkButton.vue # 收藏按钮
│   │   │   ├── Aside.vue        # 侧边栏
│   │   │   ├── Footer.vue       # 页脚
│   │   │   ├── post/            # 帖子相关组件
│   │   │   │   ├── PostForm.vue
│   │   │   │   ├── MarkdownEditor.vue
│   │   │   │   └── CommunitySelector.vue
│   │   │   ├── comment/         # 评论相关组件
│   │   │   │   ├── CommentList.vue
│   │   │   │   ├── CommentItem.vue
│   │   │   │   ├── CommentTree.vue
│   │   │   │   ├── CommentEditor.vue
│   │   │   │   └── VoteButton.vue
│   │   │   ├── community/       # 社区相关组件
│   │   │   │   ├── CommunityForm.vue
│   │   │   │   ├── CommunityInfoCard.vue
│   │   │   │   └── MemberActions.vue
│   │   │   ├── search/          # 搜索相关组件
│   │   │   │   ├── SearchResultsList.vue
│   │   │   │   └── SearchSuggestions.vue
│   │   │   ├── trending/        # 热门内容组件
│   │   │   │   ├── HotPostsList.vue
│   │   │   │   ├── HotCommunitiesList.vue
│   │   │   │   └── HotUsersList.vue
│   │   │   ├── upload/          # 上传组件
│   │   │   │   └── FileUploader.vue
│   │   │   └── user/            # 用户相关组件
│   │   │       ├── ProfileEditDialog.vue
│   │   │       └── PasswordEditDialog.vue
│   │   ├── views/              # 页面组件
│   │   │   ├── Login.vue       # 登录页
│   │   │   ├── Main.vue        # 主页
│   │   │   ├── Trending.vue    # 热门页面
│   │   │   ├── CreatePost.vue  # 发帖页
│   │   │   ├── PostDetail.vue  # 帖子详情
│   │   │   ├── CommunityDetail.vue    # 社区详情
│   │   │   ├── CreateCommunity.vue    # 创建社区
│   │   │   ├── AllCommunities.vue     # 所有社区
│   │   │   ├── MyCommunities.vue      # 我的社区
│   │   │   ├── CommunityManage.vue   # 社区管理
│   │   │   ├── CommunityMembers.vue  # 社区成员
│   │   │   ├── MyBookmarks.vue        # 我的收藏
│   │   │   ├── MyPosts.vue            # 我的帖子
│   │   │   ├── SearchResults.vue      # 搜索结果
│   │   │   ├── UserDetail.vue         # 用户详情
│   │   │   ├── Settings.vue    # 设置
│   │   │   ├── EditPost.vue    # 编辑帖子
│   │   │   └── Not-found.vue   # 404
│   │   ├── stores/             # Pinia 状态存储
│   │   │   └── user.js         # 用户状态
│   │   ├── router/             # Vue Router 配置
│   │   ├── api/                # API 客户端
│   │   ├── composables/        # Vue 组合式 API
│   │   │   ├── useTrending.ts
│   │   │   ├── useVote.ts
│   │   │   ├── useBookmark.ts
│   │   │   └── useSearch.ts
│   │   └── assets/             # 静态资源
│   ├── public/                 # 公共文件
│   ├── package.json            # 前端依赖
│   └── vite.config.js          # Vite 配置
├── main.py                     # 后端应用入口
├── requirements.txt            # Python 依赖
├── migrate_simple.sql          # 数据库迁移脚本
├── start.sh                    # 启动脚本
└── .env                        # 环境配置
```

## API 端点

### 认证相关（4个）
- `POST /api/v1/login` - 用户登录（返回 access + refresh token）
- `POST /api/v1/refresh` - 刷新访问令牌
- `POST /api/v1/logout` - 登出
- `POST /api/v1/user` - 用户注册

### 帖子相关（14个）
- `GET /api/v1/posts` - 获取帖子列表
- `GET /api/v1/posts/my` - 获取我的帖子列表
- `GET /api/v1/posts/hot` - 获取热门帖子（按热度排名）
- `GET /api/v1/posts/{post_id}` - 获取帖子详情
- `POST /api/v1/posts` - 创建帖子
- `PUT /api/v1/posts/{post_id}` - 编辑帖子
- `PATCH /api/v1/posts/{post_id}` - 部分编辑帖子
- `DELETE /api/v1/posts/{post_id}` - 软删除帖子
- `POST /api/v1/posts/{post_id}/restore` - 恢复已删除帖子
- `PATCH /api/v1/posts/{post_id}/lock` - 锁定/解锁帖子
- `PATCH /api/v1/posts/{post_id}/highlight` - 设为/取消精华
- `PATCH /api/v1/posts/{post_id}/pin` - 置顶/取消置顶
- `GET /api/v1/posts/{post_id}/bookmark-count` - 获取帖子收藏数

### 评论相关（6个）
- `GET /api/v1/posts/{post_id}/comments` - 获取嵌套评论树
- `GET /api/v1/posts/{post_id}/comments/{parent_id}/replies` - 获取子评论列表
- `POST /api/v1/comments` - 创建评论
- `PUT /api/v1/comments/{comment_id}` - 编辑评论
- `DELETE /api/v1/comments/{comment_id}` - 软删除评论
- `POST /api/v1/comments/{comment_id}/restore` - 恢复已删除评论

### 投票相关（4个）
- `POST /api/v1/vote` - 统一投票接口（帖子和评论）
- `GET /api/v1/posts/{post_id}/vote` - 获取帖子投票状态
- `GET /api/v1/comments/{comment_id}/vote` - 获取评论投票状态
- `POST /api/v1/votes/batch-status` - 批量获取投票状态

### 收藏相关（6个）
- `POST /api/v1/bookmarks` - 收藏帖子
- `DELETE /api/v1/bookmarks/{post_id}` - 取消收藏
- `GET /api/v1/bookmarks` - 获取收藏列表
- `GET /api/v1/bookmarks/my-posts` - 获取我收藏的帖子
- `GET /api/v1/bookmarks/check/{post_id}` - 检查是否已收藏
- `POST /api/v1/bookmarks/check-batch` - 批量检查收藏状态

### 上传相关（4个）
- `POST /api/v1/uploads/images` - 上传图片
- `POST /api/v1/uploads/videos` - 上传视频
- `POST /api/v1/uploads/files` - 上传普通文件
- `POST /api/v1/uploads/batch` - 批量上传文件

### 附件访问（2个）
- `GET /api/v1/attachments/{attachment_id}/presigned-url` - 获取附件访问链接
- `POST /api/v1/attachments/batch-presigned-urls` - 批量获取附件访问链接

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

### 社区相关（5个）
- `GET /api/v1/communities` - 获取社区列表
- `POST /api/v1/communities` - 创建社区
- `GET /api/v1/communities/recommend` - 社区推荐
- `GET /api/v1/communities/{name}` - 根据名字获取社区详情
- `GET /api/v1/communities/id/{community_id}` - 根据ID获取社区详情

### 社区成员相关（10个）
- `POST /api/v1/communities/{community_id}/join` - 加入社区
- `POST /api/v1/communities/{community_id}/leave` - 退出社区
- `GET /api/v1/communities/{community_id}/members` - 获取社区成员列表
- `POST /api/v1/communities/{community_id}/members/{user_id}/ban` - 封禁用户
- `POST /api/v1/communities/{community_id}/members/{user_id}/unban` - 解封用户
- `POST /api/v1/communities/{community_id}/members/{user_id}/promote` - 提升为管理员
- `POST /api/v1/communities/{community_id}/members/{user_id}/demote` - 降级为成员
- `POST /api/v1/communities/{community_id}/transfer-ownership` - 转让社区所有权
- `GET /api/v1/feed` - 获取我的动态流
- `GET /api/v1/communities/my-communities` - 获取用户加入的社区列表

### 热门内容（1个）
- `GET /api/v1/hot/sidebar` - 获取侧边栏热门内容（热门帖子、热门社区、活跃用户）

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

# 4. 收藏数据 (Hash)
bookmarks:user:{id}       # 用户收藏列表 (post_id -> {folder, note, created_at})

# 5. 投票数据 (Hash)
votes:post:{id}           # 帖子投票数据
votes:comment:{id}        # 评论投票数据
```

### 热度更新流程

```
用户交互 (投票/浏览/分享)
    ↓
Redis: 更新计数器 + 重新计算 hot_rank + 更新 ZSET
    ↓
异步任务: 每分钟批量同步到 PostgreSQL
```

### 交互权重配置

| 交互类型 | 权重 | 说明 |
|---------|------|------|
| 投票 | 10 | 权重最高，直接参与 score 计算 |
| 分享 | 5 | 中等权重，反映内容传播度 |
| 浏览 | 1 | 低权重，累计到热度 |

### 缓存策略

| 场景 | 策略 | TTL |
|------|------|-----|
| 热门列表 ZSET | 永久，实时更新 | 无 |
| 帖子详情 Hash | 缓存失效自动删除 | 10 分钟 |
| 交互计数器 | 永久，定时同步 | 无 |
| 帖子编辑/删除 | 立即失效缓存 | 立即 |
| 收藏数据 | 永久，实时更新 | 无 |

## 社区功能特性

### 自动加入机制
- 创建社区时，创建者自动成为社区拥有者（owner）
- 在某个社区中发帖时，如果用户还不是该社区成员，会自动加入后再发帖
- 社区成员角色：member（普通成员）、moderator（管理员）、owner（拥有者）

### 成员管理功能
- 封禁/解封用户
- 管理员晋升/降级
- 所有权转让

### 导航流程
- 首页动态（Home Feed）：显示所有可见帖子，支持分页
- 热门内容：显示全局热门帖子、热门社区、活跃用户
- 我的社区：显示用户已加入的社区列表
- 社区详情页：显示社区信息和社区内帖子
- 发帖页面：可预选社区或从社区详情页直接发帖

## 安全特性

- JWT 认证（Access + Refresh Token）
- Token 刷新和轮换
- Token 黑名单管理
- 密码 bcrypt 加密
- SQL 注入防护（ORM）
- XSS 防护
- CORS 配置
- 输入验证（Pydantic）
- 权限控制（作者/管理员/社区拥有者）
- 操作审计日志
- 社区封禁机制

## 待开发功能

- 实时通知（WebSocket）
- 私信功能
- 内容审核工具
- 单元测试和集成测试
- 前端 UI 完善

## 下一步建议

1. 测试功能 - 使用 Swagger UI (http://localhost:8000/docs) 测试所有 API
2. 完善前端 - 补充前端页面和交互
3. 添加测试 - 编写单元测试和集成测试
4. 部署生产 - 如需公网访问，考虑配置 Nginx + HTTPS

## 许可证

本项目仅供学习和参考使用。
