"""
@Created on : 2025/12/8
@Author: wrn
@Des: 评论路由
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from backend.models.user import User
from backend.core.security import get_current_user
from backend.core.permissions import can_comment_on_post, get_community_moderator
from backend.core.audit import create_audit_log
from backend.models.audit_log import ActionType, TargetType
from tortoise import connections
from backend.schemas import comment as schemas
from backend.models import post as models

router = APIRouter(tags=["评论相关"])


@router.post("/comments", response_model=schemas.CommentOut, summary="创建评论")

async def create_comment(
    comment_in: schemas.CommentCreate,
    current_user: User = Depends(get_current_user),
):
    # 验证帖子存在且用户可以评论
    post = await can_comment_on_post(comment_in.post_id, current_user)

    comment = await models.Comment.create(
        **comment_in.model_dump(),
        author=current_user
    )
    return comment

@router.get("/posts/{post_id}/comments", response_model=List[schemas.CommentOut],summary="获取帖子评论树")

async def get_comments_tree(post_id: int):
    """
    使用 PostgreSQL Recursive CTE (递归公用表表达式) 
    一次性获取完整的无限层级评论树
    """
    conn = connections.get("default")
    
    # --- 核心 SQL 逻辑 ---
    # 1. Anchor Member: 选出根评论 (parent_id IS NULL)
    # 2. Recursive Member: 递归关联子评论
    # 3. JOIN users: 获取作者名字
    sql = """
    WITH RECURSIVE comment_tree AS (
        -- 第一部分：种子查询（根评论）
        SELECT 
            c.id, 
            c.content, 
            c.author_id, 
            c.parent_id, 
            c.created_at, 
            u.username as author_name,
            0 as depth, 
            ARRAY[c.id] as path -- 用于排序的路径数组
        FROM comments c
        JOIN users u ON c.author_id = u.id -- 假设你的用户表叫 users
        WHERE c.post_id = $1 AND c.parent_id IS NULL
        
        UNION ALL
        
        -- 第二部分：递归查询（子评论）
        SELECT 
            c.id, 
            c.content, 
            c.author_id, 
            c.parent_id, 
            c.created_at, 
            u.username as author_name,
            ct.depth + 1, 
            ct.path || c.id
        FROM comments c
        JOIN users u ON c.author_id = u.id
        JOIN comment_tree ct ON c.parent_id = ct.id
    )
    SELECT * FROM comment_tree ORDER BY path;
    """

    # execute_query_dict 返回的是字典列表
    flat_comments = await conn.execute_query_dict(sql, [post_id])
    
    # SQL 取出来的是平铺的列表
    # 我们需要在 Python 内存中把它组装成树状结构
    return build_tree(flat_comments)


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
    current_user: User = Depends(get_current_user),
):
    """编辑评论（仅作者）"""
    comment = await models.Comment.get_or_none(id=comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权编辑此评论")

    if comment.deleted_at:
        raise HTTPException(status_code=400, detail="无法编辑已删除的评论")

    await models.Comment.filter(id=comment_id).update(
        content=comment_in.content,
        is_edited=True
    )
    await comment.refresh_from_db()

    return comment

@router.delete("/comments/{comment_id}", summary="删除评论")

async def delete_comment(
    comment_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """软删除评论（作者或管理员）,不从数据库删除，更新deleted_at为当前时间，防止删除父评论子评论变成孤儿"""
    comment = await models.Comment.get_or_none(id=comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # 权限检查
    is_author = comment.author_id == current_user.id
    is_moderator = False

    if not is_author:
        # 检查是否为版主
        post = await models.Post.get(id=comment.post_id)
        try:
            await get_community_moderator(post.community_id, current_user)
            is_moderator = True
        except HTTPException:
            pass

    if not is_author and not is_moderator and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权删除此评论")

    await models.Comment.filter(id=comment_id).update(
        deleted_at=datetime.now(timezone.utc)
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
    current_user: User = Depends(get_current_user),
):
    """恢复已删除的评论"""
    comment = await models.Comment.get_or_none(id=comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权恢复此评论")

    await models.Comment.filter(id=comment_id).update(deleted_at=None)

    return {"message": "评论恢复成功"}