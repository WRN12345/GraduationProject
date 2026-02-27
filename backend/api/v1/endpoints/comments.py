"""
@Created on : 2025/12/8
@Author: wrn
@Des: 评论路由
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from models.user import User
from models.comment import Comment
from models.post import Post
from core.security import get_current_user
from core.permissions import can_comment_on_post, get_community_moderator
from core.audit import create_audit_log
from models.audit_log import ActionType, TargetType
from tortoise import connections
from schemas import comment as schemas
from core.redis_service import comment_cache_service

router = APIRouter(tags=["评论相关"])


@router.post("/comments", response_model=schemas.CommentOut, summary="创建评论")

async def create_comment(
    comment_in: schemas.CommentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """创建评论并更新 Redis 缓存"""
    # 验证帖子存在且用户可以评论
    post = await can_comment_on_post(comment_in.post_id, current_user)

    comment = await Comment.create(
        content=comment_in.content,
        post_id=comment_in.post_id,
        author_id=current_user.id,
        parent_id=comment_in.parent_id
    )

    # 更新 Redis 缓存
    redis = request.app.state.redis

    # 1. 缓存新评论
    comment_data = {
        'id': comment.id,
        'content': comment.content,
        'author_id': comment.author_id,
        'author_name': current_user.username,
        'parent_id': comment.parent_id,
        'upvotes': comment.upvotes,
        'downvotes': comment.downvotes,
        'score': comment.score,
        'deleted_at': comment.deleted_at,
        'is_edited': comment.is_edited,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at,
    }

    await comment_cache_service.cache_comment(
        redis=redis,
        post_id=comment.post_id,
        comment_data=comment_data
    )

    # 2. 添加到索引
    await comment_cache_service.add_to_children_index(
        redis=redis,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        comment_id=comment.id,
        score=comment.score
    )

    # 构建响应
    response_data = {
        'id': comment.id,
        'content': comment.content,
        'author_id': comment.author_id,
        'author_name': current_user.username,
        'parent_id': comment.parent_id,
        'upvotes': comment.upvotes,
        'downvotes': comment.downvotes,
        'score': comment.score,
        'is_edited': comment.is_edited,
        'deleted_at': comment.deleted_at,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at,
        'replies': [],
        'reply_count': 0,
        'has_more_replies': False,
    }

    return response_data

@router.get("/posts/{post_id}/comments", summary="获取帖子评论树（懒加载）")
async def get_comments_tree(
    post_id: int,
    root_offset: int = Query(0, ge=0, description="根评论偏移量"),
    root_limit: int = Query(20, ge=1, le=100, description="根评论数量"),
    reply_limit: int = Query(3, ge=0, le=10, description="每个根评论预加载的子评论数"),
    request: Request = None
):
    """
    Redis 缓存优先的懒加载评论树

    - 首次加载：返回根评论 + 每个根评论的前 N 条子评论
    - 后续加载：通过 get_comment_replies 按需获取子评论
    - 缓存未命中：从数据库加载并重建缓存
    """
    redis = request.app.state.redis

    # 1. 尝试从 Redis 获取
    comments_tree = await comment_cache_service.get_post_comments(
        redis=redis,
        post_id=post_id,
        root_limit=root_limit,
        root_offset=root_offset,
        reply_limit=reply_limit,
        include_children=True
    )

    # 2. 如果缓存为空，从数据库加载
    if not comments_tree:
        # 2.1 使用 SQL CTE 查询所有评论
        conn = connections.get("default")
        sql = """
        WITH RECURSIVE comment_tree AS (
            SELECT
                c.id,
                c.content,
                c.author_id,
                c.parent_id,
                c.upvotes,
                c.downvotes,
                c.score,
                c.deleted_at,
                c.is_edited,
                c.created_at,
                c.updated_at,
                u.username as author_name,
                0 as depth
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = $1 AND c.parent_id IS NULL

            UNION ALL

            SELECT
                c.id,
                c.content,
                c.author_id,
                c.parent_id,
                c.upvotes,
                c.downvotes,
                c.score,
                c.deleted_at,
                c.is_edited,
                c.created_at,
                c.updated_at,
                u.username as author_name,
                ct.depth + 1
            FROM comments c
            JOIN users u ON c.author_id = u.id
            JOIN comment_tree ct ON c.parent_id = ct.id
        )
        SELECT * FROM comment_tree ORDER BY depth, created_at;
        """

        flat_comments = await conn.execute_query_dict(sql, [post_id])

        if flat_comments:
            # 2.2 重建 Redis 缓存
            await comment_cache_service.build_cache_from_db(
                redis=redis,
                post_id=post_id,
                comments_data=flat_comments
            )

            # 2.3 再次从缓存获取（这次应该命中）
            comments_tree = await comment_cache_service.get_post_comments(
                redis=redis,
                post_id=post_id,
                root_limit=root_limit,
                root_offset=root_offset,
                reply_limit=reply_limit,
                include_children=True
            )

    return comments_tree


@router.get("/posts/{post_id}/comments/{parent_id}/replies", summary="获取子评论列表")
async def get_comment_replies(
    post_id: int,
    parent_id: int,
    offset: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    request: Request = None
):
    """
    按需加载子评论（点击展开时调用）

    - 返回指定父评论的子评论列表
    - 支持分页
    - 包含每条子评论的子评论数量统计
    """
    redis = request.app.state.redis

    # 1. 尝试从 Redis 获取
    result = await comment_cache_service.get_comment_replies(
        redis=redis,
        post_id=post_id,
        parent_id=parent_id,
        offset=offset,
        limit=limit
    )

    # 2. 缓存未命中，从数据库加载
    if not result['replies']:
        # 查询子评论
        conn = connections.get("default")

        sql = """
        SELECT
            c.id,
            c.content,
            c.author_id,
            c.parent_id,
            c.upvotes,
            c.downvotes,
            c.score,
            c.deleted_at,
            c.is_edited,
            c.created_at,
            c.updated_at,
            u.username as author_name
        FROM comments c
        JOIN users u ON c.author_id = u.id
        WHERE c.post_id = $1 AND c.parent_id = $2
        ORDER BY c.score DESC, c.created_at ASC
        LIMIT $3 OFFSET $4;
        """

        replies_data = await conn.execute_query_dict(sql, [post_id, parent_id, limit, offset])

        if replies_data:
            # 重建缓存
            await comment_cache_service.build_cache_from_db(
                redis=redis,
                post_id=post_id,
                comments_data=replies_data
            )

            # 再次获取
            result = await comment_cache_service.get_comment_replies(
                redis=redis,
                post_id=post_id,
                parent_id=parent_id,
                offset=offset,
                limit=limit
            )

    return result


def build_tree(flat_data: List[Dict[str, Any]]) -> List[Dict[str, Any ]]:
    """
    将平铺的数据库结果集转换为嵌套的树状结构
    复杂度: O(N) - 只需遍历一次
    """
    # 1. 创建映射表: id -> node
    id_map = {}
    roots = []
    
    # 先把所有节点初始化
    for row in flat_data:
        # 确保 replies 列表存在
        row['replies'] = []
        # 处理时间格式 (有时候 raw sql 返回的是 str, pydantic 需要 datetime)
        # Tortoise asyncpg 通常返回 datetime 对象，这里视具体情况调整
        id_map[row['id']] = row

    # 2. 组装树
    for row in flat_data:
        parent_id = row['parent_id']
        
        if parent_id is None:
            # 根节点
            roots.append(row)
        else:
            # 子节点：找到父节点并挂载
            parent_node = id_map.get(parent_id)
            if parent_node:
                parent_node['replies'].append(row)
            else:
                # 孤儿节点处理 (理论上有了外键约束不会发生，但作为防御性编程)
                roots.append(row)

    return roots

@router.put("/comments/{comment_id}", response_model=schemas.CommentOut, summary="编辑评论")

async def update_comment(
    comment_id: int,
    comment_in: schemas.CommentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """编辑评论（仅作者）并失效缓存"""
    comment = await Comment.get_or_none(id=comment_id).prefetch_related('author')

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权编辑此评论")

    if comment.deleted_at:
        raise HTTPException(status_code=400, detail="无法编辑已删除的评论")

    await Comment.filter(id=comment_id).update(
        content=comment_in.content,
        is_edited=True
    )
    await comment.refresh_from_db()

    # 失效缓存
    redis = request.app.state.redis
    await comment_cache_service.invalidate_comment(
        redis=redis,
        post_id=comment.post_id,
        comment_id=comment_id,
        parent_id=comment.parent_id
    )

    # 构建响应数据（添加 author_name）
    return {
        'id': comment.id,
        'content': comment.content,
        'author_id': comment.author_id,
        'author_name': comment.author.username if comment.author else current_user.username,
        'parent_id': comment.parent_id,
        'upvotes': comment.upvotes,
        'downvotes': comment.downvotes,
        'score': comment.score,
        'is_edited': comment.is_edited,
        'deleted_at': comment.deleted_at,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at,
        'replies': [],
        'reply_count': 0,
        'has_more_replies': False,
    }

@router.delete("/comments/{comment_id}", summary="删除评论")

async def delete_comment(
    comment_id: int,
    request: Request,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """软删除评论（作者或管理员）并失效缓存"""
    comment = await Comment.get_or_none(id=comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # 权限检查
    is_author = comment.author_id == current_user.id
    is_moderator = False

    if not is_author:
        # 检查是否为版主
        post = await Post.get(id=comment.post_id)
        try:
            await get_community_moderator(post.community_id, current_user)
            is_moderator = True
        except HTTPException:
            pass

    if not is_author and not is_moderator and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除此评论")

    await Comment.filter(id=comment_id).update(
        deleted_at=datetime.now(timezone.utc)
    )

    # 失效缓存
    redis = request.app.state.redis
    await comment_cache_service.invalidate_comment(
        redis=redis,
        post_id=comment.post_id,
        comment_id=comment_id,
        parent_id=comment.parent_id
    )

    # 记录审计日志
    await create_audit_log(
        actor=current_user,
        target_type=TargetType.COMMENT,
        target_id=comment_id,
        action_type=ActionType.DELETE_COMMENT,
        reason=reason,
        metadata={"is_author": is_author, "is_moderator": is_moderator}
    )

    return {"message": "评论删除成功"}

@router.post("/comments/{comment_id}/restore", summary="恢复评论")
async def restore_comment(
    comment_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """恢复已删除的评论并失效缓存"""
    comment = await Comment.get_or_none(id=comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权恢复此评论")

    await Comment.filter(id=comment_id).update(deleted_at=None)

    # 失效缓存
    redis = request.app.state.redis
    await comment_cache_service.invalidate_comment(
        redis=redis,
        post_id=comment.post_id,
        comment_id=comment_id,
        parent_id=comment.parent_id
    )

    return {"message": "评论恢复成功"}