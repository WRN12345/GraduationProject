"""
@Created on : 2026.3.13
@Author: wrn
@Des: 投票服务 - Redis 缓存 + 异步落库
"""
from typing import Optional, Tuple, List
from datetime import datetime, timezone
from redis.asyncio import Redis
from models.user import User
from models.post import Post
from models.comment import Comment
from models.vote import Vote
from core.config import settings


class VoteService:
    """投票服务 - Redis + 异步落库"""

    # Redis Key 前缀
    VOTE_COUNTS_PREFIX = "vote:counts"
    VOTE_USERS_PREFIX = "vote:users"
    VOTE_VOTERS_PREFIX = "post:voters"
    SYNC_PREFIX = "vote:sync"

    @staticmethod
    def _get_counts_key(target_type: str, target_id: int) -> str:
        """获取投票计数 key"""
        return f"{VoteService.VOTE_COUNTS_PREFIX}:{target_type}:{target_id}"

    @staticmethod
    def _get_user_vote_key(user_id: int, target_type: str, target_id: int) -> str:
        """获取用户投票记录 key"""
        return f"{VoteService.VOTE_USERS_PREFIX}:{user_id}:{target_type}:{target_id}"

    @staticmethod
    def _get_voters_key(target_type: str, target_id: int, direction: str) -> str:
        """获取投票用户列表 key"""
        if target_type == "post":
            return f"{VoteService.VOTE_VOTERS_PREFIX}:{direction}:{target_id}"
        return f"comment:voters:{direction}:{target_id}"

    @staticmethod
    def _get_sync_key(target_type: str) -> str:
        """获取同步标记 key"""
        return f"{VoteService.SYNC_PREFIX}:{target_type}"

    async def get_vote_counts(
        self,
        redis: Redis,
        target_type: str,
        target_id: int
    ) -> Tuple[int, int, int]:
        """
        从 Redis 获取投票计数

        Returns:
            (upvotes, downvotes, score)
        """
        key = self._get_counts_key(target_type, target_id)
        data = await redis.hgetall(key)

        if not data:
            # Redis 没有，返回默认值
            return 0, 0, 0

        upvotes = int(data.get('upvotes', 0))
        downvotes = int(data.get('downvotes', 0))
        score = int(data.get('score', 0))

        # 确保计数永远不小于 0（修复数据一致性问题）
        upvotes = max(0, upvotes)
        downvotes = max(0, downvotes)

        return upvotes, downvotes, score

    async def get_user_vote_status(
        self,
        redis: Redis,
        user_id: int,
        target_type: str,
        target_id: int
    ) -> int:
        """
        获取用户投票状态

        Returns:
            1 (已赞), -1 (已踩), 0 (未投票)
        """
        key = self._get_user_vote_key(user_id, target_type, target_id)
        status = await redis.get(key)

        if status is not None:
            return int(status)

        # Redis 没有，查询数据库
        if target_type == "post":
            vote = await Vote.filter(
                user_id=user_id,
                post_id=target_id
            ).first()
        else:
            vote = await Vote.filter(
                user_id=user_id,
                comment_id=target_id
            ).first()

        if vote:
            status = vote.direction
            # 回写 Redis (TTL: 24小时)
            user_ttl = getattr(settings, 'REDIS_USER_VOTE_TTL', 86400)
            await redis.setex(key, user_ttl, str(status))
            return status

        return 0

    async def vote(
        self,
        redis: Redis,
        user: User,
        target_type: str,
        target_id: int,
        direction: int,
        target_created_at: Optional[datetime] = None
    ) -> dict:
        """
        投票操作（Redis 优先 + 异步落库）

        Args:
            redis: Redis 客户端
            user: 当前用户
            target_type: 'post' 或 'comment'
            target_id: 帖子/评论 ID
            direction: 1 (赞) 或 -1 (踩)
            target_created_at: 帖子创建时间（用于更新热度）

        Returns:
            操作结果
        """
        # DEBUG: 打印接收到的参数
        direction_str = "LIKE(点赞)" if direction == 1 else "DISLIKE(点踩)" if direction == -1 else f"UNKNOWN({direction})"
        print(f"[VOTE DEBUG] 收到投票请求: {direction_str}, target_type={target_type}, target_id={target_id}")

        # 0. 修复：先检查并修复 Redis 中的负数投票数
        counts_key = self._get_counts_key(target_type, target_id)
        current_data = await redis.hgetall(counts_key)

        if current_data:
            current_upvotes = int(current_data.get(b'upvotes', 0))
            current_downvotes = int(current_data.get(b'downvotes', 0))

            # 如果发现负数，立即修复
            if current_upvotes < 0 or current_downvotes < 0:
                print(f"[修复] 发现负数投票数 {target_type}:{target_id}: upvotes={current_upvotes}, downvotes={current_downvotes}")
                await redis.hset(counts_key, 'upvotes', max(0, current_upvotes))
                await redis.hset(counts_key, 'downvotes', max(0, current_downvotes))
                # 重新计算 score
                fixed_upvotes = max(0, current_upvotes)
                fixed_downvotes = max(0, current_downvotes)
                await redis.hset(counts_key, 'score', fixed_upvotes - fixed_downvotes)
                print(f"[修复] 已重置为: upvotes={fixed_upvotes}, downvotes={fixed_downvotes}")

        # 1. 检查当前投票状态
        current_status = await self.get_user_vote_status(
            redis, user.id, target_type, target_id
        )

        # 2. 确定操作类型
        if current_status == direction:
            # 重复点击 -> 取消投票
            new_status = 0
            delta = -direction
        elif current_status == 0:
            # 新投票
            new_status = direction
            delta = direction
        else:
            # 改变方向
            new_status = direction
            delta = direction - current_status

        # 3. 获取 TTL 配置
        counts_ttl = getattr(settings, 'REDIS_VOTE_COUNTS_TTL', 3600)
        user_ttl = getattr(settings, 'REDIS_USER_VOTE_TTL', 86400)
        voters_ttl = getattr(settings, 'REDIS_VOTERS_LIST_TTL', 604800)

        # 4. 更新 Redis（原子操作）
        pipe = redis.pipeline()

        # 4.1 更新用户投票状态
        user_key = self._get_user_vote_key(user.id, target_type, target_id)
        if new_status == 0:
            pipe.delete(user_key)
        else:
            pipe.setex(user_key, user_ttl, str(new_status))

        # 4.2 更新投票计数（使用 HINCRBY，但先确保不会产生负数）
        counts_key = self._get_counts_key(target_type, target_id)

        if current_status == direction:
            # 取消投票 - 需要特别小心防止负数
            if direction == 1:
                # 对于取消点赞：先读取当前值，如果 <= 0 则重置为 0 再减 1
                # 使用 Lua 脚本确保原子性
                lua_script = """
                local current = redis.call('HGET', KEYS[1], 'upvotes')
                if current == false then current = 0 end
                current = tonumber(current)
                if current <= 0 then
                    redis.call('HSET', KEYS[1], 'upvotes', 0)
                    local downvotes = redis.call('HGET', KEYS[1], 'downvotes')
                    if downvotes == false then downvotes = 0 end
                    redis.call('HSET', KEYS[1], 'score', tonumber(downvotes) * -1)
                else
                    redis.call('HINCRBY', KEYS[1], 'upvotes', -1)
                    redis.call('HINCRBY', KEYS[1], 'score', ARGV[1])
                end
                """
                pipe.eval(lua_script, 1, counts_key, -1)
            else:
                # 对于取消点踩：同样处理
                lua_script = """
                local current = redis.call('HGET', KEYS[1], 'downvotes')
                if current == false then current = 0 end
                current = tonumber(current)
                if current <= 0 then
                    redis.call('HSET', KEYS[1], 'downvotes', 0)
                    local upvotes = redis.call('HGET', KEYS[1], 'upvotes')
                    if upvotes == false then upvotes = 0 end
                    redis.call('HSET', KEYS[1], 'score', tonumber(upvotes))
                else
                    redis.call('HINCRBY', KEYS[1], 'downvotes', -1)
                    redis.call('HINCRBY', KEYS[1], 'score', ARGV[1])
                end
                """
                pipe.eval(lua_script, 1, counts_key, 1)
        elif current_status == 0:
            # 新投票 - 不会有问题，因为是从 0 开始加
            if direction == 1:
                print(f"[VOTE DEBUG] 新投票-增加 upvotes (direction=1)")
                pipe.hincrby(counts_key, 'upvotes', 1)
            else:
                print(f"[VOTE DEBUG] 新投票-增加 downvotes (direction=-1)")
                pipe.hincrby(counts_key, 'downvotes', 1)
            pipe.hincrby(counts_key, 'score', delta)
        else:
            # 改变方向 - 需要小心，但这个应该不会产生负数
            if direction == 1:
                # 从踩改为赞：downvotes--, upvotes++
                pipe.hincrby(counts_key, 'upvotes', 1)
                pipe.hincrby(counts_key, 'downvotes', -1)
            else:
                # 从赞改为踩：upvotes--, downvotes++
                pipe.hincrby(counts_key, 'upvotes', -1)
                pipe.hincrby(counts_key, 'downvotes', 1)
            pipe.hincrby(counts_key, 'score', delta)

        # 设置 TTL
        pipe.expire(counts_key, counts_ttl)

        # 4.3 更新投票用户列表
        if new_status != 0:
            voters_key = self._get_voters_key(target_type, target_id, 'up' if new_status == 1 else 'down')
            timestamp = datetime.now(timezone.utc).timestamp()
            pipe.zadd(voters_key, {str(user.id): timestamp})
            pipe.expire(voters_key, voters_ttl)

        # 4.4 如果是取消投票，从列表中移除
        if new_status == 0 and current_status != 0:
            old_voters_key = self._get_voters_key(target_type, target_id, 'up' if current_status == 1 else 'down')
            pipe.zrem(old_voters_key, str(user.id))
        elif new_status != 0 and current_status != 0 and current_status != new_status:
            # 改变方向，从旧列表移除
            old_voters_key = self._get_voters_key(target_type, target_id, 'up' if current_status == 1 else 'down')
            pipe.zrem(old_voters_key, str(user.id))

        await pipe.execute()

        # 5. 更新帖子热度（仅对帖子）
        if target_type == "post" and delta != 0 and target_created_at:
            from services.redis_service import hot_rank_service
            vote_type = 'upvote' if delta > 0 else 'downvote'
            await hot_rank_service.increment_interaction(
                redis=redis,
                post_id=target_id,
                interaction_type=vote_type,
                created_at=target_created_at
            )

        # 6. 标记需要同步到数据库
        sync_key = self._get_sync_key(target_type)
        await redis.sadd(sync_key, target_id)
        await redis.expire(sync_key, 3600)

        return {
            "status": new_status,
            "delta": delta,
            "message": "投票成功" if new_status != 0 else "已取消投票"
        }

    async def batch_get_vote_statuses(
        self,
        redis: Redis,
        user_id: int,
        items: List[Tuple[str, int]]
    ) -> dict:
        """
        批量获取投票状态

        Args:
            redis: Redis 客户端
            user_id: 用户 ID
            items: [(target_type, target_id), ...]

        Returns:
            {(target_type, target_id): status}
        """
        if not items:
            return {}

        pipe = redis.pipeline()
        for target_type, target_id in items:
            key = self._get_user_vote_key(user_id, target_type, target_id)
            pipe.get(key)

        results = await pipe.execute()

        statuses = {}
        for (target_type, target_id), status in zip(items, results):
            if status is not None:
                statuses[(target_type, target_id)] = int(status)
            else:
                statuses[(target_type, target_id)] = 0

        return statuses


# 导出服务实例
vote_service = VoteService()


__all__ = ["VoteService", "vote_service"]
