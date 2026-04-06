# 项目结构文档

本文档描述了 Super Forum System 的目录结构和文件组织。

---

## 目录结构

```
Super/
├── backend/                      # 后端代码
│   ├── api/                      # API 路由
│   │   ├── __init__.py          # FastAPI 应用初始化
│   │   └── v1/                  # API v1 版本
│   │       ├── __init__.py      # 路由注册
│   │       └── endpoints/       # API 端点
│   │           ├── login.py     # 登录、注册、刷新令牌
│   │           ├── user.py      # 用户资料、公开资料
│   │           ├── posts.py     # 帖子 CRUD、热度排名
│   │           ├── comments.py  # 评论 CRUD、嵌套评论
│   │           ├── communities.py # 社区管理
│   │           ├── memberships.py # 成员管理、封禁、管理员
│   │           ├── votes.py     # 投票系统
│   │           ├── search.py    # 全文搜索
│   │           ├── bookmarks.py # 收藏系统
│   │           ├── uploads.py   # 文件上传
│   │           ├── attachments.py # 附件访问
│   │           ├── hot.py       # 热门内容
│   │           ├── drafts.py    # 草稿管理
│   │           └── admin.py     # 超级管理员 API
│   ├── core/                    # 核心模块
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 认证和安全
│   │   ├── cache.py            # Redis 连接
│   │   ├── permissions.py      # 权限控制
│   │   ├── audit.py            # 操作审计
│   │   ├── tasks/              # 异步任务
│   │   │   ├── sync_tasks.py   # 数据同步任务
│   │   │   ├── stats_tasks.py  # 统计任务
│   │   │   └── tasks.py        # 任务调度
│   │   └── services/           # 业务服务
│   │       ├── auth/           # 认证服务
│   │       │   ├── auth_service.py
│   │       │   └── user_service.py
│   │       ├── content/        # 内容服务
│   │       │   ├── post_service.py
│   │       │   ├── comment_service.py
│   │       │   ├── community_service.py
│   │       │   ├── vote_service.py
│   │       │   ├── bookmark_service.py
│   │       │   ├── hot_content_service.py
│   │       │   ├── search_service.py
│   │       │   ├── draft_service.py
│   │       │   └── membership_service.py
│   │       ├── admin/          # 管理员服务
│   │       │   ├── admin_service.py
│   │       │   ├── audit_service.py
│   │       │   ├── stats_service.py
│   │       │   └── content_management_service.py
│   │       └── infrastructure/ # 基础设施服务
│   │           ├── upload_service.py
│   │           ├── attachment_service.py
│   │           ├── rustfs_service.py
│   │           └── redis_service.py
│   ├── models/                 # 数据库模型
│   │   ├── user.py             # 用户模型 + Karma 计算
│   │   ├── post.py             # 帖子模型 + Hot Rank 计算
│   │   ├── comment.py          # 评论模型
│   │   ├── vote.py             # 投票模型
│   │   ├── community.py        # 社区模型
│   │   ├── membership.py       # 成员模型
│   │   ├── bookmark.py         # 收藏模型
│   │   ├── post_attachment.py  # 附件模型
│   │   └── audit_log.py        # 审计日志模型
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py             # 用户相关 schemas
│   │   ├── post.py             # 帖子相关 schemas
│   │   ├── comment.py          # 评论相关 schemas
│   │   ├── vote.py             # 投票相关 schemas
│   │   ├── community.py        # 社区相关 schemas
│   │   ├── membership.py       # 成员相关 schemas
│   │   ├── bookmark.py         # 收藏相关 schemas
│   │   └── hot.py              # 热门内容 schemas
│   ├── migrations/             # 数据库迁移
│   ├── tests/                  # 测试文件
│   ├── main.py                 # 应用入口
│   ├── requirements.txt        # Python 依赖
│   └── .env                    # 环境配置
├── frontend/                    # 前端代码
│   ├── src/
│   │   ├── components/         # 可复用 Vue 组件
│   │   │   ├── Layout.vue      # 主布局
│   │   │   ├── Header.vue      # 导航头部
│   │   │   ├── PostList.vue    # 帖子列表
│   │   │   ├── PostCard.vue    # 帖子卡片
│   │   │   ├── VoteButtons.vue # 投票按钮
│   │   │   ├── BookmarkButton.vue # 收藏按钮
│   │   │   ├── Aside.vue       # 侧边栏
│   │   │   ├── Footer.vue      # 页脚
│   │   │   ├── post/           # 帖子相关组件
│   │   │   │   ├── PostForm.vue
│   │   │   │   ├── MarkdownEditor.vue
│   │   │   │   └── CommunitySelector.vue
│   │   │   ├── comment/        # 评论相关组件
│   │   │   │   ├── CommentList.vue
│   │   │   │   ├── CommentItem.vue
│   │   │   │   ├── CommentTree.vue
│   │   │   │   ├── CommentEditor.vue
│   │   │   │   └── VoteButton.vue
│   │   │   ├── community/      # 社区相关组件
│   │   │   │   ├── CommunityForm.vue
│   │   │   │   ├── CommunityInfoCard.vue
│   │   │   │   └── MemberActions.vue
│   │   │   ├── search/         # 搜索相关组件
│   │   │   │   ├── SearchResultsList.vue
│   │   │   │   └── SearchSuggestions.vue
│   │   │   ├── trending/       # 热门内容组件
│   │   │   │   ├── HotPostsList.vue
│   │   │   │   ├── HotCommunitiesList.vue
│   │   │   │   └── HotUsersList.vue
│   │   │   ├── upload/         # 上传组件
│   │   │   │   └── FileUploader.vue
│   │   │   ├── user/           # 用户相关组件
│   │   │   │   ├── ProfileEditDialog.vue
│   │   │   │   └── PasswordEditDialog.vue
│   │   │   └── admin/          # 管理员组件
│   │   │       ├── AdminHeader.vue
│   │   │       ├── AdminSidebar.vue
│   │   │       └── StatsCard.vue
│   │   ├── views/              # 页面组件
│   │   │   ├── Login.vue       # 登录页
│   │   │   ├── Trending.vue    # 热门页面
│   │   │   ├── CreatePost.vue  # 发帖页
│   │   │   ├── PostDetail.vue  # 帖子详情
│   │   │   ├── CommunityDetail.vue
│   │   │   ├── CreateCommunity.vue
│   │   │   ├── AllCommunities.vue
│   │   │   ├── MyCommunities.vue
│   │   │   ├── CommunityManage.vue
│   │   │   ├── CommunityMembers.vue
│   │   │   ├── MyBookmarks.vue
│   │   │   ├── MyPosts.vue
│   │   │   ├── MyDrafts.vue
│   │   │   ├── SearchResults.vue
│   │   │   ├── UserDetail.vue
│   │   │   ├── Settings.vue
│   │   │   ├── EditPost.vue
│   │   │   ├── Not-found.vue
│   │   │   └── admin/          # 管理员页面
│   │   │       ├── AdminDashboard.vue
│   │   │       ├── AdminUsers.vue
│   │   │       ├── AdminPosts.vue
│   │   │       ├── AdminPostDetail.vue
│   │   │       ├── AdminComments.vue
│   │   │       └── AdminActivity.vue
│   │   ├── stores/             # Pinia 状态存储
│   │   │   ├── user.js         # 用户状态
│   │   │   ├── postList.js     # 帖子列表状态
│   │   │   └── theme.js        # 主题状态
│   │   ├── router/             # Vue Router 配置
│   │   ├── api/                # API 客户端
│   │   │   ├── admin.js        # 管理员 API
│   │   │   └── attachment.js   # 附件 API
│   │   ├── composables/        # Vue 组合式 API
│   │   │   ├── useTrending.ts
│   │   │   ├── useVote.ts
│   │   │   ├── useBookmark.ts
│   │   │   ├── useSearch.ts
│   │   │   ├── useDraft.js
│   │   │   ├── useAttachment.js
│   │   │   ├── useAdminTable.js
│   │   │   └── useAdminTimeFilter.js
│   │   ├── i18n/               # 国际化
│   │   │   ├── index.js
│   │   │   ├── en.json
│   │   │   └── zh-CN.json
│   │   └── assets/             # 静态资源
│   │       ├── css/
│   │       └── image/
│   ├── public/                 # 公共文件
│   ├── package.json            # 前端依赖
│   └── vite.config.js          # Vite 配置
├── docs/                        # 文档目录
│   ├── api.md                  # API 接口文档
│   ├── features.md             # 功能模块文档
│   ├── architecture.md         # 架构设计文档
│   └── project-structure.md    # 项目结构文档（本文件）
├── main.py                      # 后端应用入口
├── requirements.txt             # Python 依赖
├── start.sh                     # 启动脚本
├── README.md                    # 项目说明
└── .gitignore                   # Git 忽略配置
```

---

## 关键文件说明

### 后端入口

| 文件 | 说明 |
|------|------|
| `backend/main.py` | FastAPI 应用入口，配置中间件和路由 |
| `backend/core/config.py` | 环境变量和应用配置 |
| `backend/core/security.py` | JWT 认证和密码处理 |

### 前端入口

| 文件 | 说明 |
|------|------|
| `frontend/src/main.js` | Vue 应用入口 |
| `frontend/src/App.vue` | 根组件 |
| `frontend/src/router/index.js` | 路由配置 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `backend/.env` | 后端环境变量 |
| `backend/requirements.txt` | Python 依赖 |
| `frontend/package.json` | 前端依赖 |
| `frontend/vite.config.js` | Vite 构建配置 |
