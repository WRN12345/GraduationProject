# 超级管理员功能架构方案

## 1. 现有架构分析

### 1.1 技术栈概览
- **后端框架**: FastAPI + Tortoise ORM (PostgreSQL)
- **缓存层**: Redis
- **对象存储**: RustFS/S3
- **认证机制**: JWT (无状态)
- **API架构**: RESTful API with versioning

### 1.2 现有模型结构

#### 用户模型 (`User`)
```python
# backend/models/user.py
- id: 主键
- username: 用户名 (唯一)
- password: 密码Hash
- nickname: 昵称
- email: 邮箱 (唯一)
- is_active: 是否激活 (可用于冻结)
- is_superuser: 是否管理员 # 已有
- karma: 声望值
- post_count: 帖子数量 (冗余)
- comment_count: 评论数量 (冗余)
- created_at: 注册时间
- last_login: 最后登录时间
```

#### 帖子模型 (`Post`)
```python
# backend/models/post.py
- id: 主键
- title: 标题
- content: Markdown内容
- community_id: 社区外键
- author_id: 作者外键
- upvotes/downvotes/score: 投票统计
- deleted_at: 软删除时间戳 # 已有
- deleted_by_id: 删除者ID # 已有
- is_locked: 锁定
- is_highlighted: 精华
- is_pinned: 置顶
```

#### 评论模型 (`Comment`)
```python
# backend/models/comment.py
- id: 主键
- content: 内容
- post_id: 帖子外键
- author_id: 作者外键
- parent_id: 父评论ID (自引用，树形结构)
- upvotes/downvotes/score: 投票统计
- deleted_at: 软删除时间戳 # 已有
- is_edited: 是否编辑
```

#### 审计日志模型 (`AuditLog`)
```python
# backend/models/audit_log.py
- id: 主键
- actor_id: 操作者外键
- target_type: 目标类型 (枚举: COMMUNITY/USER/POST/COMMENT)
- target_id: 目标ID
- action_type: 操作类型 (枚举)
- reason: 操作原因
- metadata: 额外信息 (JSON)
- created_at: 操作时间
```

**现有 `ActionType` 枚举**:
- `DELETE_POST (16)`, `RESTORE_POST (17)`
- `DELETE_COMMENT (20)`, `RESTORE_COMMENT (21)`
- `LOCK_POST (10)`, `HIGHLIGHT_POST (12)`, `PIN_POST (14)` 等

### 1.3 现有服务层

| 服务 | 路径 | 功能 |
|-----|-----|-----|
| `AuthService` | `core/services/auth/auth_service.py` | 登录/注册/刷新Token |
| `UserService` | `core/services/auth/user_service.py` | 用户信息管理/头像上传 |
| `PostService` | `core/services/content/post_service.py` | 帖子CRUD/缓存/热度 |
| `CommentService` | `core/services/content/comment_service.py` | 评论CRUD/缓存 |

### 1.4 现有API端点

| 端点 | 方法 | 功能 | 权限 |
|-----|-----|-----|-----|
| `/login` | POST | 登录 | 公开 |
| `/user` | POST | 注册 | 公开 |
| `/posts` | GET | 帖子列表 | 公开 |
| `/posts/{id}` | GET | 帖子详情 | 公开 |
| `/posts` | POST | 创建帖子 | 登录 |
| `/posts/{id}` | PUT | 编辑帖子 | 作者 |
| `/posts/{id}` | DELETE | 删除帖子 | 作者/版主/管理员 |
| `/posts/{id}/restore` | POST | 恢复帖子 | **仅超级管理员** |
| `/comments` | POST | 创建评论 | 登录 |
| `/comments/{id}` | DELETE | 删除评论 | 作者/版主/管理员 |
| `/users` | GET | 当前用户信息 | 登录 |

### 1.5 现有权限系统

```python
# backend/core/security.py
- get_current_user(): JWT认证
- get_current_admin(): 验证is_superuser # 已有

# backend/core/permissions.py
- require_superuser(): 验证超级管理员权限
- can_moderate_post(): 版主权限检查
```

### 1.6 配置

```python
# backend/core/config.py
- ADMIN_REGISTER_KEY: 管理员注册密钥 (从.env读取)
```

---

## 2. 需求分析与设计

### 2.1 需求概述

1. **超级管理员注册**: 注册时添加 `ADMIN_REGISTER_KEY` 字段，验证通过后成为管理员 ✅ **已有**
2. **管理帖子**: 
   - 管理员可以删除所有用户的帖子（不能修改）
   - 管理员可以恢复普通用户软删除的帖子
   - 管理员可以硬删除帖子
3. **管理评论**: 
   - 管理员可以删除所有用户的评论（不能修改）
   - 管理员可以恢复评论
   - 管理员可以硬删除评论
4. **操作历史**: 管理员主页显示其操作行为
5. **控制面板**: 数据统计控制面板

---

## 3. 数据库变更

### 3.1 现有模型修改

无需修改现有模型，利用现有字段即可：
- `User.is_superuser`: 标识管理员
- `Post.deleted_at`: 软删除标记
- `Comment.deleted_at`: 软删除标记
- `AuditLog`: 记录操作历史

### 3.2 新增操作类型枚举

在 `ActionType` 中新增：

```python
# backend/models/audit_log.py 新增
class ActionType(IntEnum):
    # ... 现有内容 ...
    
    # 超级管理员操作
    HARD_DELETE_POST = 18      # 硬删除帖子
    HARD_DELETE_COMMENT = 22    # 硬删除评论
    RESTORE_COMMENT = 21        # 已存在
    BAN_USER = 3                # 已存在
    UNBAN_USER = 4              # 已存在
```

---

## 4. 后端实施计划

### 4.1 需要修改的文件

| 文件 | 修改内容 |
|-----|---------|
| `backend/models/audit_log.py` | 新增 `HARD_DELETE_POST`, `HARD_DELETE_COMMENT` 枚举值 |
| `backend/core/services/content/post_service.py` | 新增 `hard_delete_post()` 方法 |
| `backend/core/services/content/comment_service.py` | 新增 `hard_delete_comment()` 方法 |
| `backend/core/services/admin/admin_service.py` | **新增** 管理员服务 (数据统计/审计日志查询) |
| `backend/api/v1/endpoints/admin.py` | **新增** 管理员API端点 |
| `backend/schemas/admin.py` | **新增** 管理员相关Schema |

### 4.2 新增文件详细设计

#### 4.2.1 管理员服务 (`backend/core/services/admin/admin_service.py`)

```python
class AdminService:
    """管理员服务 - 数据统计 + 审计日志查询"""
    
    async def get_dashboard_stats(self) -> dict:
        """获取控制面板统计数据"""
        # 用户统计
        total_users = await User.all().count()
        active_users = await User.filter(is_active=True).count()
        admin_users = await User.filter(is_superuser=True).count()
        
        # 帖子统计
        total_posts = await Post.all().count()
        active_posts = await Post.filter(deleted_at__isnull=True).count()
        deleted_posts = await Post.filter(deleted_at__isnull=False).count()
        
        # 评论统计
        total_comments = await Comment.all().count()
        active_comments = await Comment.filter(deleted_at__isnull=True).count()
        deleted_comments = await Comment.filter(deleted_at__isnull=False).count()
        
        # 社区统计
        total_communities = await Community.all().count()
        
        return {
            "users": {"total": total_users, "active": active_users, "admins": admin_users},
            "posts": {"total": total_posts, "active": active_posts, "deleted": deleted_posts},
            "comments": {"total": total_comments, "active": active_comments, "deleted": deleted_comments},
            "communities": {"total": total_communities}
        }
    
    async def get_admin_audit_logs(
        self,
        admin_user: User,
        skip: int = 0,
        limit: int = 20,
        action_type: Optional[int] = None,
        target_type: Optional[int] = None
    ) -> dict:
        """获取管理员操作历史"""
        query = AuditLog.filter(actor_id=admin_user.id)
        
        if action_type:
            query = query.filter(action_type=action_type)
        if target_type:
            query = query.filter(target_type=target_type)
        
        total = await query.count()
        logs = await query.order_by("-created_at").offset(skip).limit(limit).prefetch_related('actor')
        
        # 序列化
        items = []
        for log in logs:
            items.append({
                "id": log.id,
                "actor": {"id": log.actor.id, "username": log.actor.username},
                "target_type": log.target_type,
                "target_id": log.target_id,
                "action_type": log.action_type,
                "reason": log.reason,
                "metadata": log.metadata,
                "created_at": log.created_at
            })
        
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    
    async def get_all_deleted_posts(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """获取所有已删除帖子"""
        query = Post.filter(deleted_at__isnull=False).order_by("-deleted_at")
        total = await query.count()
        posts = await query.offset(skip).limit(limit).select_related('author', 'community')
        
        items = []
        for post in posts:
            items.append({
                "id": post.id,
                "title": post.title,
                "author": {"id": post.author.id, "username": post.author.username},
                "community": {"id": post.community.id, "name": post.community.name},
                "deleted_by_id": post.deleted_by_id,
                "deleted_at": post.deleted_at,
                "created_at": post.created_at
            })
        
        return {"items": items, "total": total}
    
    async def get_all_deleted_comments(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> dict:
        """获取所有已删除评论"""
        # ... 类似实现
```

#### 4.2.2 管理端Schema (`backend/schemas/admin.py`)

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DashboardStats(BaseModel):
    """控制面板统计数据"""
    users: dict
    posts: dict
    comments: dict
    communities: dict

class AuditLogOut(BaseModel):
    """审计日志输出"""
    id: int
    actor: dict
    target_type: int
    target_id: int
    action_type: int
    reason: Optional[str]
    metadata: dict
    created_at: datetime

class DeletedPostOut(BaseModel):
    """已删除帖子输出"""
    id: int
    title: str
    author: dict
    community: dict
    deleted_by_id: Optional[int]
    deleted_at: Optional[datetime]
    created_at: datetime

class PostHardDelete(BaseModel):
    """帖子硬删除请求"""
    post_id: int
    reason: Optional[str] = None

class CommentHardDelete(BaseModel):
    """评论硬删除请求"""
    comment_id: int
    reason: Optional[str] = None
```

#### 4.2.3 管理员API端点 (`backend/api/v1/endpoints/admin.py`)

```python
from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from models.user import User
from core.security import get_current_admin
from core.cache import get_redis
from schemas import admin as schemas
from core.services.admin.admin_service import admin_service

router = APIRouter(tags=["管理员相关"], prefix="/admin")

@router.get("/dashboard", response_model=schemas.DashboardStats, summary="控制面板统计")
async def get_dashboard(
    current_user: User = Depends(get_current_admin)
):
    """获取控制面板统计数据 (仅管理员)"""
    return await admin_service.get_dashboard_stats()

@router.get("/audit-logs", summary="获取管理员操作历史")
async def get_admin_audit_logs(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    action_type: Optional[int] = None,
    target_type: Optional[int] = None,
    current_user: User = Depends(get_current_admin)
):
    """获取当前管理员的操作历史"""
    return await admin_service.get_admin_audit_logs(
        admin_user=current_user,
        skip=skip,
        limit=limit,
        action_type=action_type,
        target_type=target_type
    )

@router.get("/posts/deleted", summary="获取所有已删除帖子")
async def get_deleted_posts(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin)
):
    """获取所有已删除帖子列表 (仅管理员)"""
    return await admin_service.get_all_deleted_posts(skip=skip, limit=limit)

@router.get("/comments/deleted", summary="获取所有已删除评论")
async def get_deleted_comments(
    skip: int = 0,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin)
):
    """获取所有已删除评论列表 (仅管理员)"""
    return await admin_service.get_all_deleted_comments(skip=skip, limit=limit)

@router.post("/posts/{post_id}/hard-delete", summary="硬删除帖子")
async def hard_delete_post(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin)
):
    """硬删除帖子 (物理删除，无法恢复)"""
    return await admin_service.hard_delete_post(
        post_id=post_id,
        user=current_user,
        reason=reason
    )

@router.post("/comments/{comment_id}/hard-delete", summary="硬删除评论")
async def hard_delete_comment(
    comment_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin)
):
    """硬删除评论 (物理删除，无法恢复)"""
    return await admin_service.hard_delete_comment(
        comment_id=comment_id,
        user=current_user,
        reason=reason
    )
```

### 4.3 API端点汇总

| 端点 | 方法 | 功能 | 权限 |
|-----|-----|-----|-----|
| `/admin/dashboard` | GET | 控制面板统计 | 仅管理员 |
| `/admin/audit-logs` | GET | 管理员操作历史 | 仅管理员 |
| `/admin/posts/deleted` | GET | 所有已删除帖子 | 仅管理员 |
| `/admin/comments/deleted` | GET | 所有已删除评论 | 仅管理员 |
| `/admin/posts/{id}/hard-delete` | POST | 硬删除帖子 | 仅管理员 |
| `/admin/comments/{id}/hard-delete` | POST | 硬删除评论 | 仅管理员 |

---

## 5. 前端实施计划

### 5.1 新增页面

| 页面 | 路径 | 功能 |
|-----|-----|-----|
| 管理员主页 | `/admin` | 控制面板展示 |
| 内容管理 | `/admin/content` | 已删除帖子/评论列表 |
| 操作历史 | `/admin/activity` | 管理员操作记录 |

### 5.2 新增组件

| 组件 | 路径 | 功能 |
|-----|-----|-----|
| `AdminDashboard.vue` | `views/AdminDashboard.vue` | 控制面板主页 |
| `StatsCard.vue` | `components/admin/StatsCard.vue` | 统计卡片 |
| `DeletedPostsList.vue` | `components/admin/DeletedPostsList.vue` | 已删除帖子列表 |
| `DeletedCommentsList.vue` | `components/admin/DeletedCommentsList.vue` | 已删除评论列表 |
| `AdminSidebar.vue` | `components/admin/AdminSidebar.vue` | 管理员侧边栏 |

### 5.3 路由配置

```javascript
// frontend/src/router/index.js 新增
{
    path: '/admin',
    component: Layout,
    meta: { requiresAdmin: true },
    children: [
        { path: '', name: 'AdminDashboard', component: () => import('../views/AdminDashboard.vue') },
        { path: 'content', name: 'AdminContent', component: () => import('../views/AdminContent.vue') },
        { path: 'activity', name: 'AdminActivity', component: () => import('../views/AdminActivity.vue') }
    ]
}
```

### 5.4 API调用设计

```javascript
// frontend/src/api/admin.js 新增
import client from './client'

export const adminApi = {
    // 控制面板统计
    getDashboard: () => client.get('/admin/dashboard'),
    
    // 操作历史
    getAuditLogs: (params) => client.get('/admin/audit-logs', { params }),
    
    // 已删除内容
    getDeletedPosts: (params) => client.get('/admin/posts/deleted', { params }),
    getDeletedComments: (params) => client.get('/admin/comments/deleted', { params }),
    
    // 硬删除
    hardDeletePost: (postId, reason) => client.post(`/admin/posts/${postId}/hard-delete`, { reason }),
    hardDeleteComment: (commentId, reason) => client.post(`/admin/comments/${commentId}/hard-delete`, { reason })
}
```

---

## 6. 实施顺序

### Phase 1: 后端基础设施
1. 修改 `audit_log.py` 新增枚举值
2. 创建 `admin_service.py` 管理员服务
3. 创建 `admin.py` Schema
4. 创建 `admin.py` API端点

### Phase 2: 帖子管理功能
1. 在 `PostService` 新增 `hard_delete_post()` 方法
2. 在 `admin.py` API端点中添加硬删除接口

### Phase 3: 评论管理功能  
1. 在 `CommentService` 新增 `hard_delete_comment()` 方法
2. 在 `admin.py` API端点中添加硬删除接口

### Phase 4: 前端开发
1. 创建管理员路由配置
2. 创建 `AdminDashboard.vue` 控制面板
3. 创建内容管理页面
4. 创建操作历史页面

### Phase 5: 测试与优化
1. 单元测试
2. 集成测试
3. 权限验证测试

---

## 7. Mermaid 流程图

### 7.1 超级管理员操作流程

```mermaid
flowchart TD
    A[管理员登录] --> B{验证成功?}
    B -->|是| C[获取Token]
    B -->|否| D[返回错误]
    
    C --> E[访问管理员端点]
    
    E --> F{操作类型}
    F -->|查看统计| G[GET /admin/dashboard]
    F -->|查看已删除帖子| H[GET /admin/posts/deleted]
    F -->|硬删除帖子| I[POST /admin/posts/{id}/hard-delete]
    F -->|查看操作历史| J[GET /admin/audit-logs]
    
    G --> K[返回统计数据]
    H --> L[返回帖子列表]
    I --> M[执行硬删除 + 审计日志]
    J --> N[返回操作记录]
    
    M --> O[删除帖子及附件]
    O --> P[创建审计日志]
    P --> Q[返回结果]
```

### 7.2 数据架构

```mermaid
erDiagram
    User {
        int id PK
        string username
        bool is_superuser
        bool is_active
    }
    
    Post {
        int id PK
        string title
        text content
        int author_id FK
        int community_id FK
        datetime deleted_at
        int deleted_by_id FK
    }
    
    Comment {
        int id PK
        text content
        int author_id FK
        int post_id FK
        datetime deleted_at
    }
    
    AuditLog {
        bigint id PK
        int actor_id FK
        int target_type
        int target_id
        int action_type
        text reason
        json metadata
        datetime created_at
    }
    
    User ||--o{ Post : author
    User ||--o{ Comment : author
    Post ||--o{ Comment : contains
    User ||--o{ AuditLog : actor
    
    AuditLog ||--|| Post : target_type=3
    AuditLog ||--|| Comment : target_type=4
```

---

## 8. 总结

本方案基于现有架构，充分利用已有的基础设施：
- ✅ `User.is_superuser` - 已有管理员标识
- ✅ `AuditLog` - 已有审计日志系统
- ✅ `Post.deleted_at` - 已有软删除机制
- ✅ `Comment.deleted_at` - 已有软删除机制
- ✅ `ADMIN_REGISTER_KEY` - 已有管理员注册机制
- ✅ `get_current_admin` - 已有管理员验证依赖

**需要新增**:
- 管理员控制面板统计功能
- 帖子/评论硬删除功能
- 管理员操作历史查询功能
- 前端管理界面

整体实施复杂度中等，主要工作量在前端界面开发。
