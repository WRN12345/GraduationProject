# API 接口文档

本文档详细描述了 Super Forum System 的所有 API 端点。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)

---

## 认证相关（4个）

### 用户登录
- **POST** `/login`
- 用户登录，返回 access + refresh token

### 刷新访问令牌
- **POST** `/refresh`
- 刷新访问令牌

### 登出
- **POST** `/logout`
- 登出，将 token 加入黑名单

### 用户注册
- **POST** `/user`
- 用户注册

---

## 帖子相关（14个）

### 获取帖子列表
- **GET** `/posts`
- 获取帖子列表

### 获取我的帖子列表
- **GET** `/posts/my`
- 获取当前用户的帖子列表

### 获取热门帖子
- **GET** `/posts/hot`
- 获取热门帖子（按热度排名）

### 获取帖子详情
- **GET** `/posts/{post_id}`
- 获取指定帖子的详细信息

### 创建帖子
- **POST** `/posts`
- 创建新帖子

### 编辑帖子
- **PUT** `/posts/{post_id}`
- 完整编辑帖子

### 部分编辑帖子
- **PATCH** `/posts/{post_id}`
- 部分编辑帖子

### 软删除帖子
- **DELETE** `/posts/{post_id}`
- 软删除帖子（标记为已删除）

### 恢复已删除帖子
- **POST** `/posts/{post_id}/restore`
- 恢复已删除的帖子

### 锁定/解锁帖子
- **PATCH** `/posts/{post_id}/lock`
- 锁定或解锁帖子

### 设为/取消精华
- **PATCH** `/posts/{post_id}/highlight`
- 设置或取消帖子精华标记

### 置顶/取消置顶
- **PATCH** `/posts/{post_id}/pin`
- 置顶或取消置顶帖子

### 获取帖子收藏数
- **GET** `/posts/{post_id}/bookmark-count`
- 获取指定帖子的收藏数量

---

## 评论相关（6个）

### 获取嵌套评论树
- **GET** `/posts/{post_id}/comments`
- 获取帖子的嵌套评论树

### 获取子评论列表
- **GET** `/posts/{post_id}/comments/{parent_id}/replies`
- 获取指定父评论的子评论列表

### 创建评论
- **POST** `/comments`
- 创建新评论

### 编辑评论
- **PUT** `/comments/{comment_id}`
- 编辑评论内容

### 软删除评论
- **DELETE** `/comments/{comment_id}`
- 软删除评论

### 恢复已删除评论
- **POST** `/comments/{comment_id}/restore`
- 恢复已删除的评论

---

## 投票相关（4个）

### 统一投票接口
- **POST** `/vote`
- 统一投票接口（支持帖子和评论）

### 获取帖子投票状态
- **GET** `/posts/{post_id}/vote`
- 获取当前用户对帖子的投票状态

### 获取评论投票状态
- **GET** `/comments/{comment_id}/vote`
- 获取当前用户对评论的投票状态

### 批量获取投票状态
- **POST** `/votes/batch-status`
- 批量获取多个目标的投票状态

---

## 收藏相关（6个）

### 收藏帖子
- **POST** `/bookmarks`
- 收藏指定帖子

### 取消收藏
- **DELETE** `/bookmarks/{post_id}`
- 取消收藏帖子

### 获取收藏列表
- **GET** `/bookmarks`
- 获取当前用户的收藏列表

### 获取我收藏的帖子
- **GET** `/bookmarks/my-posts`
- 获取当前用户收藏的帖子详情

### 检查是否已收藏
- **GET** `/bookmarks/check/{post_id}`
- 检查指定帖子是否已被收藏

### 批量检查收藏状态
- **POST** `/bookmarks/check-batch`
- 批量检查多个帖子的收藏状态

---

## 上传相关（4个）

### 上传图片
- **POST** `/uploads/images`
- 上传图片（最大 10MB）

### 上传视频
- **POST** `/uploads/videos`
- 上传视频（最大 100MB）

### 上传普通文件
- **POST** `/uploads/files`
- 上传普通文件（最大 50MB）

### 批量上传文件
- **POST** `/uploads/batch`
- 批量上传文件（自动分类）

---

## 附件访问（2个）

### 获取附件访问链接
- **GET** `/attachments/{attachment_id}/presigned-url`
- 获取附件的 Presigned URL（24小时有效期）

### 批量获取附件访问链接
- **POST** `/attachments/batch-presigned-urls`
- 批量获取多个附件的 Presigned URL

---

## 用户相关（6个）

### 获取当前用户
- **GET** `/users`
- 获取当前登录用户信息（需认证）

### 更新个人资料
- **PUT** `/users`
- 更新当前用户的个人资料（需认证）

### 获取公开用户资料
- **GET** `/users/{username}`
- 根据用户名获取公开的用户资料

### 获取用户的帖子
- **GET** `/users/{username}/posts`
- 获取指定用户发布的帖子

### 获取用户的评论
- **GET** `/users/{username}/comments`
- 获取指定用户发布的评论

### 获取用户活动汇总
- **GET** `/users/{username}/activity`
- 获取指定用户的活动汇总信息

---

## 搜索相关（5个）

### 全文搜索帖子
- **GET** `/search/posts`
- 全文搜索帖子（支持中文分词）

### 搜索评论
- **GET** `/search/comments`
- 搜索评论（支持中文分词）

### 搜索用户
- **GET** `/search/users`
- 搜索用户（按用户名/昵称）

### 统一搜索
- **GET** `/search/all`
- 统一搜索（帖子+评论+用户）

### 搜索建议
- **GET** `/search`
- 搜索建议（快速预览）

---

## 社区相关（5个）

### 获取社区列表
- **GET** `/communities`
- 获取所有社区列表

### 创建社区
- **POST** `/communities`
- 创建新社区

### 社区推荐
- **GET** `/communities/recommend`
- 根据帖子内容智能推荐社区

### 根据名字获取社区详情
- **GET** `/communities/{name}`
- 根据社区名称获取社区详情

### 根据ID获取社区详情
- **GET** `/communities/id/{community_id}`
- 根据社区ID获取社区详情

---

## 社区成员相关（10个）

### 加入社区
- **POST** `/communities/{community_id}/join`
- 加入指定社区

### 退出社区
- **POST** `/communities/{community_id}/leave`
- 退出指定社区

### 获取社区成员列表
- **GET** `/communities/{community_id}/members`
- 获取指定社区的成员列表

### 封禁用户
- **POST** `/communities/{community_id}/members/{user_id}/ban`
- 封禁指定用户

### 解封用户
- **POST** `/communities/{community_id}/members/{user_id}/unban`
- 解封指定用户

### 提升为管理员
- **POST** `/communities/{community_id}/members/{user_id}/promote`
- 将成员提升为社区管理员

### 降级为成员
- **POST** `/communities/{community_id}/members/{user_id}/demote`
- 将管理员降级为普通成员

### 转让社区所有权
- **POST** `/communities/{community_id}/transfer-ownership`
- 转让社区所有权给其他成员

### 获取我的动态流
- **GET** `/feed`
- 获取用户关注社区的动态流

### 获取用户加入的社区列表
- **GET** `/communities/my-communities`
- 获取当前用户加入的所有社区

---

## 热门内容（1个）

### 获取侧边栏热门内容
- **GET** `/hot/sidebar`
- 获取侧边栏热门内容（热门帖子、热门社区、活跃用户）

---

## 草稿相关（5个）

### 获取草稿列表
- **GET** `/drafts`
- 获取当前用户的草稿列表

### 获取草稿详情
- **GET** `/drafts/{draft_id}`
- 获取指定草稿的详细信息

### 创建草稿
- **POST** `/drafts`
- 创建新草稿

### 更新草稿
- **PUT** `/drafts/{draft_id}`
- 更新草稿内容

### 删除草稿
- **DELETE** `/drafts/{draft_id}`
- 删除指定草稿

---

## 超级管理员相关（17个）

### 获取控制面板统计数据
- **GET** `/admin/dashboard`
- 获取管理员控制面板的统计数据

### 获取用户列表
- **GET** `/admin/users`
- 获取用户列表（支持搜索、筛选）

### 获取用户详情
- **GET** `/admin/users/{user_id}`
- 获取指定用户的详细信息

### 冻结用户
- **POST** `/admin/users/{user_id}/ban`
- 冻结指定用户账号

### 解冻用户
- **POST** `/admin/users/{user_id}/unban`
- 解冻指定用户账号

### 获取帖子列表
- **GET** `/admin/posts`
- 获取帖子列表（支持搜索、包含已删除）

### 获取帖子详情
- **GET** `/admin/posts/{post_id}`
- 获取指定帖子的详细信息

### 软删除帖子
- **DELETE** `/admin/posts/{post_id}`
- 软删除指定帖子

### 恢复帖子
- **POST** `/admin/posts/{post_id}/restore`
- 恢复已删除的帖子

### 硬删除帖子
- **DELETE** `/admin/posts/{post_id}/hard`
- 永久删除帖子（不可恢复）

### 获取评论列表
- **GET** `/admin/comments`
- 获取评论列表（支持搜索、包含已删除）

### 软删除评论
- **DELETE** `/admin/comments/{comment_id}`
- 软删除指定评论

### 恢复评论
- **POST** `/admin/comments/{comment_id}/restore`
- 恢复已删除的评论

### 硬删除评论
- **DELETE** `/admin/comments/{comment_id}/hard`
- 永久删除评论（不可恢复）

### 获取审计日志列表
- **GET** `/admin/audit-logs`
- 获取管理员操作日志列表

### 操作类型统计
- **GET** `/admin/stats/action-stats`
- 获取操作类型统计数据

### 操作趋势
- **GET** `/admin/stats/trend`
- 获取操作趋势数据

---

## 错误响应

所有 API 在发生错误时返回统一的错误格式：

```json
{
  "detail": "错误描述信息"
}
```

常见的 HTTP 状态码：

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器内部错误 |
