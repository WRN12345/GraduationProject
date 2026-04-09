# Super Forum System - 仿 Reddit 社区论坛系统

一个功能完整的 Reddit 风格社区论坛系统，基于 FastAPI + Vue 3 + PostgreSQL + Redis 构建。

## 项目简介

Super Forum System 是一个现代化的社区论坛平台，提供了完整的社区管理、内容发布、互动交流等功能。系统采用前后端分离架构，后端使用 FastAPI 提供高性能 API 服务，前端使用 Vue 3 构建响应式用户界面。

## 核心特性

- 🔐 **用户认证** - JWT 双令牌认证机制
- 🏘️ **社区管理** - 创建、加入、管理社区
- 📝 **内容发布** - Markdown 格式帖子、嵌套评论
- 🗳️ **投票系统** - 帖子和评论点赞/踩
- 🔖 **收藏系统** - 帖子收藏和分类管理
- 🔥 **热度排名** - Reddit 经典热度算法
- 🔍 **全文搜索** - PostgreSQL 中文分词搜索
- 📁 **文件上传** - 图片、视频、附件上传
- 👮 **管理后台** - 完整的超级管理员系统

## 技术栈

### 后端
- **FastAPI 0.104+** - 现代、快速的 Python Web 框架
- **PostgreSQL 14+** - 关系型数据库
- **Tortoise ORM** - 异步 ORM
- **Redis 7+** - 内存数据库（缓存和热度排行）
- **JWT** - JSON Web Tokens 认证

### 前端
- **Vue 3.5+** - 渐进式 JavaScript 框架
- **TypeScript 5.9+** - 类型安全的 JavaScript
- **Vite 7.2+** - 快速构建工具
- **Element Plus 2.12+** - Vue 3 UI 组件库
- **Pinia 2.3+** - Vue 状态管理

## 📚 文档

详细文档请查看 [`docs/`](docs/) 目录：

| 文档 | 说明 |
|------|------|
| [API 接口文档](docs/api.md) | 所有 API 端点的详细说明 |
| [功能模块文档](docs/features.md) | 各功能模块的详细介绍 |
| [架构设计文档](docs/architecture.md) | 技术架构和设计决策 |
| [项目结构文档](docs/project-structure.md) | 目录结构和文件组织 |


